package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"time"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Uso: go run debug-missing-commit.go <patch_id>")
		os.Exit(1)
	}
	
	patchID := os.Args[1]
	repoPath := "/Users/drestrepo/Documents/groups/mccartney/incursor-back-loan-account-service"
	
	fmt.Printf("=== Debug para patch-id: %s ===\n", patchID)
	fmt.Printf("Repositorio: %s\n\n", repoPath)
	
	ctx := context.Background()
	analyzer := NewGitAnalyzer(repoPath)
	
	// 1. Buscar commits con este patch-id
	fmt.Println("1. Buscando commits con este patch-id...")
	
	// Obtener todos los commits del repo
	allRefs, err := analyzer.listRefs(ctx)
	if err != nil {
		log.Fatal(err)
	}
	
	// Filtrar refs relevantes
	targetRef, err := analyzer.detectTargetRef(ctx)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("   Target ref: %s\n", targetRef)
	
	// Obtener commits del target
	targetCommits, err := analyzer.revList(ctx, targetRef)
	if err != nil {
		log.Fatal(err)
	}
	
	// Obtener otras refs
	otherRefs := filterRefs(allRefs, otherPatterns)
	var otherCommits []string
	for _, ref := range otherRefs {
		if ref == targetRef {
			continue
		}
		refCommits, err := analyzer.revList(ctx, ref)
		if err != nil {
			continue
		}
		otherCommits = append(otherCommits, refCommits...)
	}
	
	fmt.Printf("   Target commits: %d\n", len(targetCommits))
	fmt.Printf("   Other commits: %d\n", len(otherCommits))
	
	// 2. Buscar commits que generan este patch-id
	fmt.Println("\n2. Verificando patch-ids...")
	var matchingCommits []string
	
	allCommits := append(targetCommits, otherCommits...)
	fmt.Printf("   Verificando %d commits...\n", len(allCommits))
	
	for i, commit := range allCommits {
		if i%100 == 0 {
			fmt.Printf("   Progreso: %d/%d\n", i, len(allCommits))
		}
		
		pid, err := analyzer.getPatchID(ctx, commit)
		if err != nil {
			continue
		}
		
		if pid == patchID {
			matchingCommits = append(matchingCommits, commit)
			fmt.Printf("   ✅ Encontrado: %s -> %s\n", commit[:12], pid[:12])
		}
	}
	
	if len(matchingCommits) == 0 {
		fmt.Printf("   ❌ No se encontraron commits con patch-id %s\n", patchID)
		return
	}
	
	fmt.Printf("\n   Total commits con este patch-id: %d\n", len(matchingCommits))
	
	// 3. Analizar cada par de commits
	fmt.Println("\n3. Analizando pares de commits...")
	
	for i, commit1 := range matchingCommits {
		for j, commit2 := range matchingCommits {
			if i >= j {
				continue
			}
			
			fmt.Printf("\n   Par: %s vs %s\n", commit1[:12], commit2[:12])
			
			// Obtener metadatos
			meta1, err := analyzer.getCommitMeta(ctx, commit1)
			if err != nil {
				fmt.Printf("   ❌ Error obteniendo meta1: %v\n", err)
				continue
			}
			
			meta2, err := analyzer.getCommitMeta(ctx, commit2)
			if err != nil {
				fmt.Printf("   ❌ Error obteniendo meta2: %v\n", err)
				continue
			}
			
			fmt.Printf("   Commit1: %s <%s> @ %s\n", meta1.AuthorName, meta1.AuthorEmail, meta1.AuthorDate.Format(time.RFC3339))
			fmt.Printf("   Commit2: %s <%s> @ %s\n", meta2.AuthorName, meta2.AuthorEmail, meta2.AuthorDate.Format(time.RFC3339))
			
			// Verificar filtros paso a paso
			fmt.Println("\n   Verificando filtros:")
			
			// Filtro 1: Autores diferentes
			sameEmail := meta1.AuthorEmail == meta2.AuthorEmail
			sameName := meta1.AuthorName == meta2.AuthorName
			
			fmt.Printf("   - Email igual: %v (%s vs %s)\n", sameEmail, meta1.AuthorEmail, meta2.AuthorEmail)
			fmt.Printf("   - Nombre igual: %v (%s vs %s)\n", sameName, meta1.AuthorName, meta2.AuthorName)
			
			if sameEmail || sameName {
				fmt.Printf("   ❌ FILTRADO: Autores iguales (email: %v, nombre: %v)\n", sameEmail, sameName)
				continue
			}
			
			// Filtro 2: Fechas
			fmt.Printf("   - Fecha1: %s\n", meta1.AuthorDate.Format(time.RFC3339))
			fmt.Printf("   - Fecha2: %s\n", meta2.AuthorDate.Format(time.RFC3339))
			
			// Determinar cuál debería ser target vs other basado en las refs
			isCommit1InTarget := contains(targetCommits, commit1)
			isCommit2InTarget := contains(targetCommits, commit2)
			
			fmt.Printf("   - Commit1 en target: %v\n", isCommit1InTarget)
			fmt.Printf("   - Commit2 en target: %v\n", isCommit2InTarget)
			
			if isCommit1InTarget && !isCommit2InTarget {
				// commit1 es target, commit2 es other
				if meta1.AuthorDate.Before(meta2.AuthorDate) {
					fmt.Printf("   ❌ FILTRADO: Target es anterior (target: %s < other: %s)\n", 
						meta1.AuthorDate.Format(time.RFC3339), meta2.AuthorDate.Format(time.RFC3339))
					continue
				}
				fmt.Printf("   ✅ VÁLIDO: Target posterior o igual (target: %s >= other: %s)\n",
					meta1.AuthorDate.Format(time.RFC3339), meta2.AuthorDate.Format(time.RFC3339))
			} else if !isCommit1InTarget && isCommit2InTarget {
				// commit2 es target, commit1 es other
				if meta2.AuthorDate.Before(meta1.AuthorDate) {
					fmt.Printf("   ❌ FILTRADO: Target es anterior (target: %s < other: %s)\n", 
						meta2.AuthorDate.Format(time.RFC3339), meta1.AuthorDate.Format(time.RFC3339))
					continue
				}
				fmt.Printf("   ✅ VÁLIDO: Target posterior o igual (target: %s >= other: %s)\n",
					meta2.AuthorDate.Format(time.RFC3339), meta1.AuthorDate.Format(time.RFC3339))
			} else {
				fmt.Printf("   ⚠️  AMBOS EN MISMO TIPO DE REF - saltando\n")
				continue
			}
			
			fmt.Printf("   🎯 COMMIT SOSPECHOSO VÁLIDO\n")
		}
	}
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}
