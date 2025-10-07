package main

import (
	"fmt"
	"time"
)

func main() {
	// Fechas problemáticas encontradas
	dates := []string{
		"2024-09-16T16:00:11Z",         // Con Z
		"2024-09-13T17:37:06-05:00",   // Con zona horaria
		"2024-04-09T12:37:41-05:00",   // Otro ejemplo
		"2023-12-19T13:49:51Z",        // Caso que funciona
	}
	
	fmt.Println("=== Test de parsing de fechas ===")
	
	for _, dateStr := range dates {
		fmt.Printf("\nFecha: %s\n", dateStr)
		
		// Probar RFC3339
		if date, err := time.Parse(time.RFC3339, dateStr); err != nil {
			fmt.Printf("  RFC3339: ERROR - %v\n", err)
		} else {
			fmt.Printf("  RFC3339: OK - %v\n", date)
		}
		
		// Probar otras alternativas
		layouts := []string{
			time.RFC3339,
			time.RFC3339Nano,
			"2006-01-02T15:04:05Z07:00",
			"2006-01-02T15:04:05-07:00",
		}
		
		parsed := false
		for _, layout := range layouts {
			if date, err := time.Parse(layout, dateStr); err == nil {
				fmt.Printf("  %s: OK - %v\n", layout, date)
				parsed = true
				break
			}
		}
		
		if !parsed {
			fmt.Printf("  NO SE PUDO PARSEAR\n")
		}
	}
}
