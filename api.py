<?php
// Enable CORS
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, HEAD, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Content-Type: application/json');

// Function to get current UTC timestamp
function getCurrentUTCTimestamp() {
    return gmdate('Y-m-d H:i:s');
}

// Function to fetch content from URL
function fetchFromUrl($url) {
    try {
        $context = stream_context_create([
            'http' => [
                'timeout' => 30,
                'user_agent' => 'Mozilla/5.0 (compatible; PHP Script)'
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        if ($response !== false) {
            return array_filter(explode("\n", $response), function($line) {
                return trim($line) !== '';
            });
        }
        error_log("Failed to fetch data from {$url}");
        return [];
    } catch (Exception $e) {
        error_log("Error fetching data: " . $e->getMessage());
        return [];
    }
}

// Function to get a random item from an array
function getRandomItem($array) {
    if (empty($array)) return null;
    return $array[array_rand($array)];
}

// Main request handling
function handleRequest() {
    // Get current UTC timestamp and user login
    $currentTimestamp = getCurrentUTCTimestamp();
    $userLogin = 'codex-ML';
    
    // Check for registration number
    $regno = $_GET['regno'] ?? null;
    
    if (!$regno) {
        http_response_code(400);
        echo json_encode([
            'error' => 'Missing registration number (regno)',
            'timestamp' => $currentTimestamp,
            'user' => $userLogin
        ]);
        return;
    }

    // URLs for proxies and user agents
    $proxiesUrl = 'https://raw.githubusercontent.com/codex-ML/proxy/refs/heads/main/abc.txt';
    $userAgentsUrl = 'https://raw.githubusercontent.com/codex-ML/proxy/refs/heads/main/useragent.txt';

    // Fetch both proxies and user agents
    $proxies = fetchFromUrl($proxiesUrl);
    $userAgents = fetchFromUrl($userAgentsUrl);

    // Get random proxy and user agent
    $randomProxy = !empty($proxies) ? getRandomItem($proxies) : null;
    $randomUserAgent = !empty($userAgents) ? getRandomItem($userAgents) : 'Mozilla/5.0 (compatible; PHP Script)';

    $apiUrl = "https://saadhanapi.cars24.team/api/v1/vahan/{$regno}";

    try {
        // Initialize cURL session
        $ch = curl_init();

        // Set cURL options
        curl_setopt_array($ch, [
            CURLOPT_URL => $apiUrl,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_FOLLOWLOCATION => true,
            CURLOPT_HTTPHEADER => [
                'User-Agent: ' . $randomUserAgent,
                'Content-Type: application/json'
            ],
            CURLOPT_TIMEOUT => 30,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_SSL_VERIFYPEER => false,
            CURLOPT_SSL_VERIFYHOST => false
        ]);

        // Set proxy if available
        if ($randomProxy) {
            curl_setopt($ch, CURLOPT_PROXY, $randomProxy);
            curl_setopt($ch, CURLOPT_PROXYTYPE, CURLPROXY_HTTP);
        }

        // Execute the request
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        // Check for cURL errors
        if (curl_errno($ch)) {
            throw new Exception(curl_error($ch));
        }

        curl_close($ch);

        // Handle the response
        if ($httpCode === 200) {
            // Decode the JSON response
            $responseData = json_decode($response, true);
            
            // Add metadata to the response
            $responseData['metadata'] = [
                'timestamp' => $currentTimestamp,
                'user' => $userLogin,
                'user_agent' => $randomUserAgent,
                'total_proxies' => count($proxies),
                'total_user_agents' => count($userAgents)
            ];
            
            // Encode and output the modified response
            echo json_encode($responseData, JSON_PRETTY_PRINT);
        } else {
            http_response_code($httpCode);
            echo json_encode([
                'error' => "API request failed with status code {$httpCode}",
                'timestamp' => $currentTimestamp,
                'user' => $userLogin,
                'user_agent' => $randomUserAgent,
                'total_proxies' => count($proxies),
                'total_user_agents' => count($userAgents)
            ], JSON_PRETTY_PRINT);
        }

    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode([
            'error' => "Request failed: " . $e->getMessage(),
            'timestamp' => $currentTimestamp,
            'user' => $userLogin,
            'user_agent' => $randomUserAgent,
            'total_proxies' => count($proxies),
            'total_user_agents' => count($userAgents)
        ], JSON_PRETTY_PRINT);
    }
}

// Handle OPTIONS request for CORS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Handle the request
handleRequest();
