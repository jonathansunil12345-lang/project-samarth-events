#!/bin/bash

echo "Testing Sample Prompts via API..."
echo "=================================="

# Test 1
echo -e "\n1. Testing: Compare rainfall + Maize crops"
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Compare the average annual rainfall in Karnataka and Maharashtra for the last 5 years. List the top 3 most produced crops of Maize in each of those states during the same period."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✓ SUCCESS' if 'Compared rainfall' in data['answer'] else '✗ FAILED'); print('Intent:', data.get('debug', {}).get('intent', 'N/A'))"

# Test 2  
echo -e "\n2. Testing: District extremes Tamil Nadu/Kerala Rice"
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Which districts in Tamil Nadu and Kerala had the highest and lowest production of Rice in 2021?"}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✓ SUCCESS' if 'peak output' in data['answer'] else '✗ FAILED'); print('Intent:', data.get('debug', {}).get('intent', 'N/A'))"

# Test 3
echo -e "\n3. Testing: Wheat trend Punjab"
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show the production trend of Wheat in Punjab over the last 5 years and compare it with the rainfall trend."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✓ SUCCESS' if 'recorded a' in data['answer'] else '✗ FAILED'); print('Intent:', data.get('debug', {}).get('intent', 'N/A'))"

# Test 4
echo -e "\n4. Testing: Policy millet vs sugarcane"
curl -s -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Should we promote millet over sugarcane in Maharashtra? Give policy arguments using climate data."}' \
  | python3 -c "import sys, json; data=json.load(sys.stdin); print('✓ SUCCESS' if 'Supporting a shift' in data['answer'] else '✗ FAILED'); print('Intent:', data.get('debug', {}).get('intent', 'N/A'))"

echo -e "\n=================================="
echo "All tests completed!"
