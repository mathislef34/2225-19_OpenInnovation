#!/bin/bash

echo "=== Démarrage de n8n en arrière-plan"
n8n start &

echo "=== Attente que n8n soit prêt"
until curl -s http://localhost:5678/healthz | grep "ok"; do
  sleep 1
done

echo "=== Import du workflow via CLI"
n8n import:workflow --input /home/node/workflows/workflow.json

echo "=== Import terminé, maintien du container"
wait
