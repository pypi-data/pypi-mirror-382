# Fluid Attacks Core Library

<p align="center">
  <img alt="logo" src="https://res.cloudinary.com/fluid-attacks/image/upload/f_auto,q_auto/v1/airs/menu/Logo?_a=AXAJYUZ0.webp" />
</p>

Get more information about this library on the
[official documentation](https://help.fluidattacks.com/portal/en/kb/articles/core-library)


69e99862c380cf0affa0e18446b9ce78f952c07c,2044d563696f2f7509ede4f752f534c525cd033a,Yunior Orlando Martinez Cordoba <ymartinez@fgs.co>,Yunior Orlando Martinez Cordoba,ymartinez@fgs.co,2025-06-16T22:13:58Z,,continuous-hacking,ecedfaef8ab1a8fd89b14d729f17036b79e6a11a,David Calle Daza <dcalle@fgs.co>,David Calle Daza,dcalle@fgs.co,2025-06-16T22:13:58Z,,refs/tags/v1.32.0,cpc-user-service,17,4,0


target=2044d563696f2f7509ede4f752f534c525cd033a
other=ecedfaef8ab1a8fd89b14d729f17036b79e6a11a

echo "== Presencia local de objetos =="
for c in $target $other; do
  if git cat-file -e $c^{commit} 2>/dev/null; then
    echo "$c: OK (commit existe localmente)"
  else
    echo "$c: FALTA (no está en .git/objects)"
  fi
done | cat

echo
echo "== 1) Identidad completa, autor/committer y fechas (FULLER) =="
git show --no-patch --pretty=fuller $target | cat
git show --no-patch --pretty=fuller $other  | cat

echo
echo "== 2) Encabezado RAW del objeto commit =="
git cat-file -p $target | head -n 60 | cat
git cat-file -p $other  | head -n 60 | cat

echo
echo "== 3) Mensajes de commit =="
echo "--- target ---"
git log -1 --format=%B $target | cat
echo "--- other ---"
git log -1 --format=%B $other  | cat

echo
echo "== 4) Padres y topología =="
git rev-list --parents -n1 $target | cat
git rev-list --parents -n1 $other  | cat

echo
echo "== 5) patch-id estable (mismo diff => mismo patch-id) =="
echo "--- target patch-id ---"
git show $target -p --pretty=format: | git patch-id --stable | cat
echo "--- other patch-id ---"
git show $other  -p --pretty=format: | git patch-id --stable | cat

echo
echo "== 6) Estadísticas de diff (adiciones/borrados) =="
git diff --stat ${target}^! | cat
git diff --stat ${other}^!  | cat

echo
echo "== 7) ¿Qué refs LOCALES contienen cada commit? =="
echo "--- branches locales con target ---"
git branch --contains $target | cat
echo "--- tags locales con target ---"
git tag --contains $target | cat

echo "--- branches locales con other ---"
git branch --contains $other | cat
echo "--- tags locales con other ---"
git tag --contains $other | cat

echo
echo "== 8) Fechas en epoch para comparar fácil =="
echo "--- target ---"
git log -1 $target --format='AuthorDate: %at  CommitDate: %ct' | cat
echo "--- other ---"
git log -1 $other  --format='AuthorDate: %at  CommitDate: %ct' | cat

echo
echo "== 9) Autor vs Committer (quién reescribió) =="
git log -1 $target --format='Author: %an <%ae> | Committer: %cn <%ce>' | cat
git log -1 $other  --format='Author: %an <%ae> | Committer: %cn <%ce>' | cat
