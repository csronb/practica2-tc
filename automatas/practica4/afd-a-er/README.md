# Expresiones Regulares de los 5 AFD seleccionados (Ejercicio 1)
| Archivo `.jff` | Ejercicio origen | ER obtenida en JFLAP (eliminación de estados) | ER simplificada |
| :--- | :--- | :--- | :--- |
| `ej254_termina_en_1.jff` | `ej254` | `0*1(1+00*1)*` | `(0+1)*1` |
| `ej255_ciclo_par_b.jff` | `ej255` | `((0+1)1*0)*` | `((0+1)1*0)*` |
| `ej256_ternario.jff` | `ej256` | `(1+2)*0(0+1+2(1+2)*0)*` | `(1+2)*0(0+1+2(1+2)*0)*` |
| `ej257_tres_estados_bc.jff` | `ej257` | `((1+01*0)(0+1))*01*+((1+01*0)(0+1))*(1+01*0)` | `((1+01*0)(0+1))*(01*+1+01*0)` |
| `ej258_tres_estados_c.jff` | `ej258` | `(0+1)(01+(1+00)(0+1))*` | `(0+1)(01+(1+00)(0+1))*` |
