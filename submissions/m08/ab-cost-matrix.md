# Matriz A/B: diez corridas oficiales

Costos estimados a partir del uso real transcrito: GPT-4o, USD 2,50/M de entrada y USD 10/M de salida, sin descuento de caché. Incluye todas las llamadas de modelo de cada corrida.

| Caso | Arquitectura | Ejecución | Exactitud | Llamadas | Tokens entrada | Tokens salida | Estimación USD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| M8-01 | A | 494 | Correcta | 5 | 5008 | 145 | 0.0139700 |
| M8-01 | B | 497 | Correcta | 5 | 5008 | 145 | 0.0139700 |
| M8-02 | A | 500 | Correcta | 3 | 2117 | 59 | 0.0058825 |
| M8-02 | B | 503 | Correcta | 3 | 2117 | 59 | 0.0058825 |
| M8-03 | A | 506 | Correcta | 4 | 7562 | 166 | 0.0205650 |
| M8-03 | B | 510 | Correcta | 4 | 7562 | 166 | 0.0205650 |
| M8-04 | A | 514 | Correcta | 4 | 7587 | 131 | 0.0202775 |
| M8-04 | B | 518 | Correcta | 4 | 6525 | 102 | 0.0173325 |
| M8-05 | A | 522 | Correcta | 5 | 5086 | 138 | 0.0140950 |
| M8-05 | B | 525 | Correcta | 5 | 5080 | 132 | 0.0140200 |

Total: 42 llamadas, 54.895 tokens y USD 0,14656 estimados. A: USD 0,07479; B: USD 0,07177. Proyección de modelo para 1.000 ejecuciones: A USD 14,958; B USD 14,354.

La estimación no es el cargo de Gateway. El agregado de USD 0,16 incluye desarrollo y no se asigna a estas diez corridas. La comparación mantiene el resultado independiente 5/5 en ambos brazos y el baseline M5 de 2/5.
