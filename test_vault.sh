curl -X POST http://localhost:3000/proxy/ingest \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Testing the automated context tagging feature.",
       "category": "System Integration",
       "tags": ["test", "integration"]
     }'