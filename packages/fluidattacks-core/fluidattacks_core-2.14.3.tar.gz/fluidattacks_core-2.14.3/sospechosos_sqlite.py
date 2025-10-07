#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detecta 'autores latentes' leyendo SOLO una DB SQLite exportada con mergestat.
- Sin invocar comandos git.
- Usa patch_id si existe (tabla opcional commit_patch_id(commit, patch_id)).
- Si no existe, calcula un fingerprint estable a partir de stats_by_commit.

Uso:
  TARGET_REF=<ref|rev> python3 sospechoso_from_sqlite.py repo.sqlite
"""

import os
import sys
import sqlite3
import hashlib
from datetime import datetime

ENV_TARGET = os.environ.get("TARGET_REF") or os.environ.get("TARGET_BRANCH")

OTHER_GLOBS = [
    # mismos patrones que tu script original
    "refs/merge-requests/%/head",
    "refs/merge-requests/%/merge",
    "refs/pull/%/head",
    "refs/pull/%/merge",
    "refs/pull-requests/%/from",
    "refs/pull-requests/%/merge",
    "refs/keep-around/%",
    "refs/remotes/origin/mr/%",
    "refs/remotes/origin/mr-merge/%",
    "refs/remotes/origin/pr/%",
    "refs/remotes/origin/pr-merge/%",
    "refs/remotes/origin/bb-pr/%",
    "refs/remotes/origin/bb-merge/%",
    "refs/remotes/origin/keep-around/%",
]

DDL = """
CREATE TABLE IF NOT EXISTS latent_authors (
    patch_id TEXT,
    target_commit TEXT,
    target_author TEXT,
    target_author_name TEXT,
    target_author_email TEXT,
    target_date TEXT,
    target_message TEXT,
    target_ref TEXT,
    other_commit TEXT,
    other_author TEXT,
    other_author_name TEXT,
    other_author_email TEXT,
    other_date TEXT,
    other_message TEXT,
    other_ref TEXT,
    target_additions INTEGER,
    target_deletions INTEGER,
    diference_days INTEGER
);
CREATE INDEX IF NOT EXISTS idx_latent_patch ON latent_authors(patch_id);
CREATE INDEX IF NOT EXISTS idx_latent_target_commit ON latent_authors(target_commit);
CREATE INDEX IF NOT EXISTS idx_latent_other_commit ON latent_authors(other_commit);
"""


def detect_target_ref(cur):
    # 0) si env var
    if ENV_TARGET:
        return ENV_TARGET

    # 1) origin/HEAD (si aparece como ref simbólica en la exportación)
    #    algunos exports no incluyen HEAD simbólico, así que probamos candidatos.
    candidates = [
        "refs/remotes/origin/HEAD",
        "origin/main",
        "refs/remotes/origin/main",
        "refs/heads/main",
        "origin/master",
        "refs/remotes/origin/master",
        "refs/heads/master",
    ]
    # Normalizamos a full_name si hace falta
    for c in candidates:
        row = cur.execute(
            "SELECT full_name FROM refs WHERE full_name = ? OR name = ? LIMIT 1", (c, c)
        ).fetchone()
        if row:
            return row[0]
    # 2) rama más reciente por fecha de commit del tip
    row = cur.execute("""
        SELECT r.full_name
        FROM refs r
        JOIN commits c ON c.hash = r.hash
        ORDER BY c.committer_when DESC
        LIMIT 1
    """).fetchone()
    return row[0] if row else None


def like_any(column, patterns):
    # construye un WHERE ... (col LIKE ? OR col LIKE ? ...)
    clauses = " OR ".join([f"{column} LIKE ?" for _ in patterns])
    return clauses, [
        p.replace("%", "\\%") for p in patterns
    ]  # escapamos si se usa wildcards manuales


def load_commits(cur):
    # commit -> metadatos
    commits = {}
    for row in cur.execute("""
        SELECT hash, message, author_name, author_email, author_when
        FROM commits
    """):
        h, msg, an, ae, ad = row
        commits[h] = {
            "message": msg or "",
            "author_name": an or "",
            "author_email": ae or "",
            "author_when": ad,
        }
    return commits


def load_commit_refs(cur):
    # mapping commit -> set(refs) desde commits_by_ref
    mapping = {}
    for row in cur.execute("SELECT ref, commit FROM commits_by_ref"):
        ref, commit = row
        mapping.setdefault(commit, set()).add(ref)
    return mapping


def load_added_deleted(cur):
    # totales por commit para reporting
    sums = {}
    for row in cur.execute("""
        SELECT commit, COALESCE(SUM(additions),0), COALESCE(SUM(deletions),0)
        FROM stats_by_commit
        GROUP BY commit
    """):
        sums[row[0]] = (int(row[1]), int(row[2]))
    return sums


def load_patch_ids_if_any(cur):
    # tabla opcional precomputada
    try:
        rows = cur.execute("SELECT commit, patch_id FROM commit_patch_id").fetchall()
        return {c: p for c, p in rows}
    except sqlite3.Error:
        return {}


def compute_stats_fingerprint(cur):
    # fingerprint pobre-pero-útil desde stats_by_commit
    # clave = SHA256 de "file_path|+a|-d\n" ordenado por file_path
    fp = {}
    sql = """
      SELECT commit, file_path, additions, deletions
      FROM stats_by_commit
      ORDER BY commit, file_path
    """
    last = None
    acc = []
    for commit, path, add, dele in cur.execute(sql):
        if commit != last and last is not None:
            digest = hashlib.sha256("\n".join(acc).encode("utf-8")).hexdigest()
            fp[last] = digest
            acc = []
        acc.append(f"{path}|+{add}|-{dele}")
        last = commit
    if last is not None:
        digest = hashlib.sha256("\n".join(acc).encode("utf-8")).hexdigest()
        fp[last] = digest
    return fp


def main(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # asegurar tabla de salida
    for stmt in DDL.strip().split(");"):
        s = stmt.strip()
        if s:
            cur.execute(s + ");")
    conn.commit()

    target_ref = detect_target_ref(cur)
    if not target_ref:
        print("No se pudo detectar TARGET_REF (pasa TARGET_REF=...)", file=sys.stderr)
        sys.exit(2)

    # otras refs según patrones
    # usamos LIKE con comodines; en SQLite '_' y '%' son wildcards
    patterns = OTHER_GLOBS
    where, args = like_any("full_name", patterns)
    other_refs = [
        r for (r,) in cur.execute(f"SELECT full_name FROM refs WHERE {where}", patterns)
    ]
    other_refs = sorted(set([r for r in other_refs if r != target_ref]))

    commits = load_commits(cur)
    commit_refs = load_commit_refs(cur)
    adddel = load_added_deleted(cur)

    # patch-id real si existe; si no, fingerprint por stats
    patch_ids = load_patch_ids_if_any(cur)
    if not patch_ids:
        patch_ids = compute_stats_fingerprint(cur)

    # índice patch -> commits
    patch_to_commits = {}
    for c, pid in patch_ids.items():
        patch_to_commits.setdefault(pid, []).append(c)

    # helper: ¿commit pertenece a target_ref?
    def in_target(c):
        return target_ref in commit_refs.get(c, set())

    suspicious_rows = []

    for pid, commits_with_pid in patch_to_commits.items():
        if len(commits_with_pid) <= 1:
            continue

        tgt = [c for c in commits_with_pid if in_target(c)]
        oth = [c for c in commits_with_pid if not in_target(c)]
        if not tgt or not oth:
            continue

        for tc in tgt:
            tm = commits.get(tc, {})
            t_name, t_email = tm.get("author_name", ""), tm.get("author_email", "")
            t_when = tm.get("author_when")
            t_date = datetime.fromisoformat(t_when) if t_when else None
            t_add, t_del = adddel.get(tc, (0, 0))

            for oc in oth:
                om = commits.get(oc, {})
                o_name, o_email = om.get("author_name", ""), om.get("author_email", "")
                o_when = om.get("author_when")
                o_date = datetime.fromisoformat(o_when) if o_when else None

                # mismo autor -> skip
                if o_email == t_email or o_name == t_name:
                    continue
                # si target es anterior al otro, asumimos original -> skip
                if t_date and o_date and t_date < o_date:
                    continue

                # primera ref asociada para reporting
                o_ref = next(iter(commit_refs.get(oc, {"unknown"})))
                suspicious_rows.append(
                    (
                        pid,
                        tc,
                        f"{t_name} <{t_email}>",
                        t_name,
                        t_email,
                        t_when or "",
                        tm.get("message", ""),
                        target_ref,
                        oc,
                        f"{o_name} <{o_email}>",
                        o_name,
                        o_email,
                        o_when or "",
                        om.get("message", ""),
                        o_ref,
                        t_add,
                        t_del,
                        (t_date - o_date).days if t_date and o_date else None,
                    )
                )

    # persistir
    cur.executemany(
        """
      INSERT INTO latent_authors (
        patch_id, target_commit, target_author, target_author_name, target_author_email,
        target_date, target_message, target_ref, other_commit, other_author, other_author_name,
        other_author_email, other_date, other_message, other_ref, target_additions,
        target_deletions, diference_days
      ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,
        suspicious_rows,
    )
    conn.commit()
    conn.close()

    print(
        f"OK. Insertados {len(suspicious_rows)} casos en latent_authors (DB: {db_path})"
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Uso: TARGET_REF=<ref|rev> python3 sospechoso_from_sqlite.py repo.sqlite",
            file=sys.stderr,
        )
        sys.exit(2)
    main(sys.argv[1])
