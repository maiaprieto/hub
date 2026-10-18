# Formato de los datos de Hub

La app lee `data.enc.json`, que es este JSON cifrado con `tools/hubcrypt.py`
(AES-256-GCM, clave derivada con PBKDF2-SHA256, 600 000 iteraciones).
El JSON en claro **nunca** se sube al repositorio.

```jsonc
{
  "updated": "2026-10-19T08:00:00+02:00",      // última actualización (cualquier pestaña)
  "hoy": {
    "updated": "…",
    "entregas":      [{ "id", "titulo", "asignatura", "fecha": "YYYY-MM-DD", "hora"?, "detalle"?, "enlace"? }],
    "cambios":       [{ "id", "titulo", "fecha", "detalle"?, "enlace"? }],   // aula, horario, prácticas
    "oportunidades": [{ "id", "titulo", "tipo", "lugar"?, "fecha"?: "YYYY-MM-DD", "detalle"?, "enlace"? }],
    "avisos":        [{ "id", "titulo", "fecha", "resumen", "enlace"? }],
    "correos":       [{ "id", "de", "asunto", "fecha", "resumen", "enlace"? }], // personas que esperan respuesta
    "eventos":       [{ "id", "titulo", "inicio": "YYYY-MM-DD", "fin"?, "hora"?, "lugar"? }]
  },
  "empleo": {
    "updated": "…",
    "candidaturas":  [{ "id", "empresa", "puesto", "estado", "fecha", "detalle"?, "enlace"? }],
    "ofertas":       [{ "id", "puesto", "empresa", "ubicacion", "modalidad"?, "nivel", "area", "fuente", "fecha", "prioridad": 1-9, "porque", "enlace" }],
    "quizas":        [{ …igual que ofertas…, "falta": "qué criterio no cumple" }]
  }
}
```

Reglas:

- `id` debe ser estable entre actualizaciones (la app guarda en el móvil qué está
  hecho, guardado u oculto usando ese id). Usar `gm-<threadId>` para Gmail,
  `cal-<eventId>` para el calendario y `li-<jobId>` para LinkedIn.
- `prioridad`: 1 = Región de Murcia, más alto = más lejos.
- Los enlaces solo pueden ser `https://`.

Comandos:

```bash
HUB_KEY='…' python3 tools/hubcrypt.py decrypt data.enc.json > /tmp/data.json
HUB_KEY='…' python3 tools/hubcrypt.py encrypt /tmp/data.json data.enc.json
```
