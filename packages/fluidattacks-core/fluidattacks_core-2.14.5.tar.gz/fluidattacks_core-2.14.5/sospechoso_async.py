#!/usr/bin/env python3
"""
Auditor de "autores latentes" robusto a clones mirror/bare y a falta de origin/main.
- Detecta automáticamente la rama objetivo (TARGET_REF) si no está definida.
- Soporta clones normales (refs/remotes/origin/*) y mirror/bare (refs/heads/*, refs/pull/*, refs/merge-requests/*, refs/keep-around/*).
- Empareja commits equivalentes por patch-id y reporta si el autor difiere entre la rama objetivo y otras refs (MR/PR/keep-around).

Uso:
  TARGET_REF=<ref O revision> python3 sospechoso_async.py > latent_authors.csv
Ejemplos:
  TARGET_REF=refs/remotes/origin/main python3 sospechoso_async.py
  TARGET_REF=refs/heads/main                 # en repos mirror/bare
  # sin TARGET_REF, intenta autodetectar.
"""

import asyncio
import base64
import subprocess
from contextlib import suppress
import json
from datetime import datetime
import sys
import csv
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path

from async_lru import alru_cache

# Permite compat con versiones previas
ENV_TARGET = os.environ.get("TARGET_REF") or os.environ.get("TARGET_BRANCH")

# Globs de refs "otras" (no la rama objetivo) para buscar equivalencias del parche
OTHER_PATTERNS = [
    # Espacio con "origin/" (clones no-bare)
    "refs/remotes/origin/mr/*",
    "refs/remotes/origin/mr-merge/*",
    "refs/remotes/origin/pr/*",
    "refs/remotes/origin/pr-merge/*",
    "refs/remotes/origin/bb-pr/*",
    "refs/remotes/origin/bb-merge/*",
    "refs/remotes/origin/keep-around/*",
    "refs/merge-requests/*/head",
    "refs/merge-requests/*/merge",
    "refs/pull/*/head",
    "refs/pull/*/merge",
    "refs/pull-requests/*/from",
    "refs/pull-requests/*/merge",
    "refs/keep-around/*",
]

# Semáforo para limitar procesos Git simultáneos
sem = asyncio.Semaphore(16 * 100)  # reducido para evitar BlockingIOError


async def run(
    cmd: list[str],
    repo_path: str,
    input_bytes: bytes | None = None,
) -> bytes:
    # """Ejecuta un comando git de forma asíncrona."""
    async with sem:  # Limitar procesos Git simultáneos
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if input_bytes else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_path,
        )
        stdout, _ = await proc.communicate(input_bytes)
        if proc.returncode and proc.returncode != 0:  # Ensure returncode is not None
            raise subprocess.CalledProcessError(proc.returncode, cmd)
        return stdout


async def commit_numstat(commit: str, repo_path: str) -> Tuple[int, int]:
    """Devuelve el total de líneas añadidas y eliminadas para *commit*."""
    try:
        out = (await run(["git", "show", "--numstat", "--format=", commit], repo_path)).decode()
    except Exception:
        return 0, 0

    added = deleted = 0
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        a_str, d_str = parts[0], parts[1]
        try:
            added += 0 if a_str == "-" else int(a_str)
            deleted += 0 if d_str == "-" else int(d_str)
        except ValueError:
            # Línea no parseable (p.e. renames con "-\t-\tfile")
            continue
    return added, deleted


async def rev_parse_verify(name: str, repo_path: str) -> str | None:
    """Devuelve el commit id si la revisión existe."""
    with suppress(subprocess.CalledProcessError):
        out = await run(["git", "rev-parse", "--verify", "-q", f"{name}^{{commit}}"], repo_path)
        return out.decode().strip()
    return None


async def list_refs(patterns: list[str], repo_path: str) -> list[str]:
    """Lista las referencias que coinciden con los patrones proporcionados."""
    cmd = ["git", "for-each-ref", "--format=%(refname)"]
    out = (await run(cmd, repo_path)).decode().splitlines()
    return [r.strip() for r in out if r.strip()]


async def detect_target_ref(repo_path: str) -> str | None:
    """Elige una ref objetivo razonable si no se especifica."""
    # 0) Si el clon tiene un archivo .info.json con "branch", usarlo
    info_path = Path(repo_path) / ".info.json"
    if info_path.is_file():
        try:
            with open(info_path) as f:
                data = json.load(f)
            branch = data.get("branch")
            if branch:
                # Probar refs/remotes/origin/<branch> primero
                cand = f"refs/remotes/origin/{branch}"
                if await rev_parse_verify(cand, repo_path):
                    return cand
                if await rev_parse_verify(branch, repo_path):
                    return branch
        except Exception:
            pass  # fallback a heurísticas

    # 1) origin/HEAD simbólico (forma completa)
    with suppress(subprocess.CalledProcessError):
        ref = (
            (await run(["git", "symbolic-ref", "-q", "refs/remotes/origin/HEAD"], repo_path))
            .decode()
            .strip()
        )
        if await rev_parse_verify(ref, repo_path):
            return ref

    candidates = [
        "origin/main",
        "refs/remotes/origin/main",
        "refs/heads/main",
        "origin/master",
        "refs/remotes/origin/master",
        "refs/heads/master",
    ]
    for c in candidates:
        if await rev_parse_verify(c, repo_path):
            # Devuelve el nombre original (rev-list acepta ambos formatos)
            return c

    # 4) HEAD simbólico (en bare normalmente apunta a refs/heads/<default>)
    with suppress(subprocess.CalledProcessError):
        head_ref = (await run(["git", "symbolic-ref", "-q", "HEAD"], repo_path)).decode().strip()
        if await rev_parse_verify(head_ref, repo_path):
            return head_ref

    # 5) El head más reciente
    with suppress(subprocess.CalledProcessError):
        out = (
            (
                await run(
                    [
                        "git",
                        "for-each-ref",
                        "--sort=-committerdate",
                        "--format=%(refname)",
                        "refs/heads/*",
                        "refs/remotes/origin/*",
                    ],
                    repo_path,
                )
            )
            .decode()
            .splitlines()
        )
        for r in out:
            if await rev_parse_verify(r, repo_path):
                return r
    return None


async def rev_list(rev: str, repo_path: str) -> list[str]:
    out = await run(["git", "rev-list", "--no-merges", rev], repo_path)
    return [x.strip().decode() for x in out.splitlines()]


@alru_cache(ttl=600)
async def commit_meta(commit: str, repo_path: str) -> dict[str, str]:
    """Obtiene metadatos de un commit."""
    fmt = "%H%x09%an%x09%ae%x09%ad%x09%D"
    out = (
        (
            await run(
                ["git", "show", "-s", "--no-color", "--date=iso-strict", "--format=" + fmt, commit],
                repo_path,
            )
        )
        .decode()
        .strip()
    )
    parts = out.split("\t")
    # Cuando un commit no tiene decoraciones, añadir elementos vacíos
    while len(parts) < 4:
        parts.append("")

    h, an, ae, ad = parts[:4]

    # Obtener el mensaje del commit
    # try:
    #     msg_out = (
    #         (
    #             await run(
    #                 ["git", "show", "-s", "--no-color", "--format=%B", commit],
    #                 repo_path,
    #             )
    #         )
    #         .decode(errors="ignore")
    #         .strip()
    #     )
    # except Exception:
    #     msg_out = ""

    return {
        "commit": h,
        "author_name": an,
        "author_email": ae,
        "author_date": ad,
        "commit_message": "",
    }


async def patch_id(commit: str, repo_path: str) -> str | None:
    """Obtiene el patch-id de un commit."""
    show = await run(["git", "show", "--no-color", "-U0", commit], repo_path)
    try:
        patch = (
            await run(
                ["git", "patch-id", "--stable"],
                repo_path,
                input_bytes=show,
            )
        ).decode()
        pid = patch.split()[0]
        return pid
    except Exception as exc:
        return None


async def main_async(root_nickname: str, repo_path: str) -> List[Dict[str, Any]]:
    """
    Detecta autores latentes usando una estructura de datos directa:
    1. Lista de commits del target (rama Fluid)
    2. Diccionario de commits -> refs donde aparecen
    3. Diccionario de patch_id -> commits que coinciden
    """
    # Detectar ref objetivo
    target_ref = ENV_TARGET or await detect_target_ref(repo_path)
    if not target_ref:
        return []
    if not await rev_parse_verify(target_ref, repo_path):
        # Intento: si viene como "origin/main", prueba también a expandir a ref completa.
        fallback = f"refs/remotes/{target_ref}" if not target_ref.startswith("refs/") else None
        if fallback and not await rev_parse_verify(fallback, repo_path):
            # Mensaje útil con listado de refs disponibles
            refs = (
                (await run(["git", "for-each-ref", "--format=%(refname)"], repo_path))
                .decode()
                .splitlines()
            )
            sys.stderr.write(
                f"\n[ERROR] La revisión '{target_ref}' no existe. Algunas refs disponibles:\n"
                + "\n".join(refs[:50])
                + ("\n..." if len(refs) > 50 else "")
                + "\n",
            )
            raise SystemExit(2)
        if fallback:
            target_ref = fallback

    # 1. Obtener lista de commits del target
    target_commits = await rev_list(target_ref, repo_path)
    if not target_commits:
        raise SystemExit(f"No hay commits en {target_ref} (o no es una rama válida).")

    # Obtener otras refs (MR/PR/keep-around)
    other_refs = await list_refs(OTHER_PATTERNS, repo_path)
    # Eliminar posibles duplicados y evitar comparar contra la misma ref objetivo
    other_refs = sorted({r for r in other_refs if r != target_ref})

    # 2. Construir diccionario de commit -> refs
    commit_to_refs = defaultdict(set)

    # Añadir commits del target a la estructura
    for commit in target_commits:
        commit_to_refs[commit].add(target_ref)

    # Añadir commits de otras refs
    for ref in other_refs:
        ref_commits = await rev_list(ref, repo_path)
        for commit in ref_commits:
            commit_to_refs[commit].add(ref)

    # 3. Construir diccionario de patch_id -> commits
    patch_to_commits = defaultdict(list)

    # Procesar todos los commits en paralelo para obtener patch_id
    all_commits = list(commit_to_refs.keys())
    pid_tasks = [patch_id(c, repo_path) for c in all_commits]
    pid_results = await asyncio.gather(*pid_tasks)

    # Construir índice de patch_id -> commits
    for commit, pid in zip(all_commits, pid_results, strict=False):
        if pid:
            patch_to_commits[pid].append(commit)

    # Buscar sospechosos: commits con mismo patch_id pero diferentes autores
    suspicious = []

    async def check_commit_pair(
        pid: str, target_commit: str, other_commit: str
    ) -> dict[str, Any] | None:
        """Procesa un par de commits para verificar si hay autoría sospechosa"""
        target_meta = await commit_meta(target_commit, repo_path)
        other_meta = await commit_meta(other_commit, repo_path)

        target_auth_name = target_meta["author_name"]
        target_auth_email = target_meta["author_email"]
        other_auth_name = other_meta["author_name"]
        other_auth_email = other_meta["author_email"]

        # Verificar si son autores diferentes
        if other_auth_email == target_auth_email or other_auth_name == target_auth_name:
            return None

        # Verificar fechas: si el commit del target es anterior al otro, no es sospechoso
        # porque el autor del target sería el original
        target_date = datetime.fromisoformat(target_meta["author_date"])
        other_date = datetime.fromisoformat(other_meta["author_date"])

        if target_date < other_date:
            # El commit del target es el original o simultáneo, no hay problema
            return None

        # Diferentes autores, añadir a sospechosos
        tgt_add, tgt_del = await commit_numstat(target_commit, repo_path)

        # Resolver refs a string para CSV
        target_ref_str = target_ref
        other_refs_set = commit_to_refs[other_commit]
        other_ref_str = next(iter(other_refs_set)) if other_refs_set else "unknown"

        return {
            "patch_id": pid,
            "target_commit": target_commit,
            "target_author": f"{target_auth_name} <{target_auth_email}>",
            "target_author_name": target_auth_name,
            "target_author_email": target_auth_email,
            "target_date": target_meta["author_date"],
            "target_message": base64.b64encode(
                target_meta.get("commit_message", "").encode("utf-8")
            ).decode("utf-8"),
            "target_ref": target_ref_str,
            "other_commit": other_commit,
            "other_author": f"{other_auth_name} <{other_auth_email}>",
            "other_author_name": other_auth_name,
            "other_author_email": other_auth_email,
            "other_date": other_meta["author_date"],
            "other_message": base64.b64encode(
                other_meta.get("commit_message", "").encode("utf-8")
            ).decode("utf-8"),
            "other_ref": other_ref_str,
            "target_additions": tgt_add,
            "target_deletions": tgt_del,
            "diference_days": (target_date - other_date).days,
            "root_nickname": root_nickname,
        }

    # Crear todas las tareas para procesar
    tasks = []
    for pid, commits_with_pid in patch_to_commits.items():
        if len(commits_with_pid) <= 1:
            continue  # No hay equivalentes

        # Dividir commits entre target y otros
        target_commits_with_pid = [c for c in commits_with_pid if target_ref in commit_to_refs[c]]
        other_commits_with_pid = [
            c for c in commits_with_pid if target_ref not in commit_to_refs[c]
        ]

        # Crear tareas para todas las comparaciones
        for target_commit in target_commits_with_pid:
            for other_commit in other_commits_with_pid:
                tasks.append(check_commit_pair(pid, target_commit, other_commit))

    # Procesar resultados a medida que se completen
    for future in asyncio.as_completed(tasks):
        result = await future
        if result:
            suspicious.append(result)

    return suspicious


async def main() -> None:
    """Punto de entrada asincrónico principal."""
    group_name = "mccartney" if len(sys.argv) == 1 else sys.argv[1]
    target_dir = Path(f"/Users/drestrepo/Documents/groups/{group_name}/")
    with open(f"results_{group_name}.csv", "w") as file:
        w = csv.DictWriter(
            file,
            fieldnames=[
                "patch_id",
                "target_commit",
                "target_author",
                "target_author_name",
                "target_author_email",
                "target_date",
                "target_message",
                "target_ref",
                "other_commit",
                "other_author",
                "other_author_name",
                "other_author_email",
                "other_date",
                "other_message",
                "other_ref",
                "root_nickname",
                "target_additions",
                "target_deletions",
                "diference_days",
            ],
        )
        w.writeheader()

        # Preprocesar directorios y crear tareas para cada repositorio
        repos = []
        for f in target_dir.iterdir():
            if f.is_dir():
                name, path = f.name, str(f.absolute())

                print(f"Processing repository {name} at {path}")
                suspicious = await main_async(name, path)
                for row in suspicious:
                    w.writerow(row)
                    file.flush()

                print(f"Processed repository {name} with {len(suspicious)} suspicious commits")


if __name__ == "__main__":
    asyncio.run(main())
