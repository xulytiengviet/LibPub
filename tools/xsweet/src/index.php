<?php

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Content-Type: text/plain; charset=utf-8');
    echo "LibPub XSweet ready\n";
    exit;
}

if (!isset($_FILES['input']) || $_FILES['input']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    exit('A valid DOCX upload named input is required.');
}

$saxonProcessor = new Saxon\SaxonProcessor();
$xsltProcessor = $saxonProcessor->newXsltProcessor();
$tmp = sys_get_temp_dir() . '/xsweet-' . bin2hex(random_bytes(8));
$inputDir = $tmp . '/input';
$outputFile = $tmp . '/output.html';
mkdir($inputDir, 0700, true);

function removeTree($directory) {
    if (!is_dir($directory)) return;
    $items = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($directory, FilesystemIterator::SKIP_DOTS),
        RecursiveIteratorIterator::CHILD_FIRST
    );
    foreach ($items as $item) {
        $item->isDir() ? rmdir($item->getPathname()) : unlink($item->getPathname());
    }
    rmdir($directory);
}

try {
    $zip = new ZipArchive();
    if ($zip->open($_FILES['input']['tmp_name']) !== true) {
        throw new RuntimeException('The uploaded file is not a readable DOCX archive.');
    }
    for ($index = 0; $index < $zip->numFiles; $index++) {
        $entry = $zip->getNameIndex($index);
        if ($entry === false || strpos($entry, '../') !== false || substr($entry, 0, 1) === '/') {
            throw new RuntimeException('DOCX contains an unsafe archive path.');
        }
    }
    if (!$zip->extractTo($inputDir)) {
        throw new RuntimeException('Could not extract DOCX.');
    }
    $zip->close();
    $documentXml = $inputDir . '/word/document.xml';
    if (!is_file($documentXml)) {
        throw new RuntimeException('DOCX is missing word/document.xml.');
    }
    $steps = [
        ['xsl/EXTRACT-docx.xsl', $documentXml, $outputFile],
        'xsl/hyperlink-inferencer.xsl',
        'xsl/PROMOTE-lists.xsl',
        'xsl/header-promotion-CHOOSE.xsl',
        'xsl/final-rinse.xsl',
        'xsl/editoria-tune.xsl',
        'xsl/p-split-around-br.xsl',
        'xsl/editoria-notes.xsl',
        'xsl/editoria-basic.xsl',
        'xsl/editoria-reduce.xsl'
    ];
    foreach ($steps as $step) {
        if (!is_array($step)) $step = [$step, $outputFile, $outputFile];
        list($xsl, $input, $output) = $step;
        $xsltProcessor->compileFromFile($xsl);
        $xsltProcessor->setSourceFromFile($input);
        $xsltProcessor->setOutputFile($output);
        $xsltProcessor->transformToFile();
        $xsltProcessor->clearParameters();
        $xsltProcessor->clearProperties();
    }
    header('Content-Type: text/html; charset=utf-8');
    readfile($outputFile);
} catch (Throwable $error) {
    http_response_code(422);
    echo $error->getMessage();
} finally {
    removeTree($tmp);
}
