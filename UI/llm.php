<?php
header('Content-Type: application/json');

$rawInput = file_get_contents('php://input');
$data = json_decode($rawInput, true);

$question = isset($data['question']) ? trim($data['question']) : '';

if ($question === '') {
    echo json_encode([
        'success' => false,
        'error'   => 'Empty question'
    ]);
    exit;
}

$payload = json_encode(['question' => $question]);

$python = 'C:\Users\zhangy85\AppData\Local\Programs\Python\Python312\python.exe';
$script = __DIR__ . DIRECTORY_SEPARATOR . 'llm_qa.py';
$cmd = "\"$python\" \"$script\"";

$descriptorSpec = [
    0 => ["pipe", "r"],  // stdin
    1 => ["pipe", "w"],  // stdout
    2 => ["pipe", "w"],  // stderr
];

$process = proc_open($cmd, $descriptorSpec, $pipes, __DIR__);

if (!is_resource($process)) {
    echo json_encode([
        'success' => false,
        'error'   => 'Failed to start Python process'
    ]);
    exit;
}

fwrite($pipes[0], $payload);
fclose($pipes[0]);

$llmOutput = stream_get_contents($pipes[1]);
fclose($pipes[1]);

$llmError = stream_get_contents($pipes[2]);
fclose($pipes[2]);

$returnCode = proc_close($process);

if ($returnCode !== 0) {
    echo json_encode([
        'success' => false,
        'error'   => 'Python exited with code ' . $returnCode,
        'details' => $llmOutput . "\n" . $llmError
    ]);
    exit;
}

$answer = trim($llmOutput);

if ($answer === '') {
    echo json_encode([
        'success' => false,
        'error'   => 'LLM returned empty answer'
    ]);
    exit;
}

echo json_encode([
    'success' => true,
    'answer'  => $answer
]);
