<?php

if (php_sapi_name() !== 'cli') {
    exit("The update script must be run from the command line.\n");
}

// The list follows the XSweet DOCX-to-HTML service supplied with LibPub.
// Stylesheets are fetched at image start so the conversion chain remains
// attributable to the upstream XSweet/HTMLevator projects.
$urls = [
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/EXTRACT-docx.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/docx-html-extract.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/docx-table-extract.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/handle-notes.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/scrub.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/join-elements.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/docx-extract/collapse-paragraphs.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/local-fixup/hyperlink-inferencer.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/list-promote/PROMOTE-lists.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/list-promote/itemize-lists.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/list-promote/mark-lists.xsl',
    'https://gitlab.coko.foundation/XSweet/HTMLevator/raw/master/applications/header-promote/header-promotion-CHOOSE.xsl',
    'https://gitlab.coko.foundation/XSweet/HTMLevator/raw/master/applications/header-promote/make-header-mapper-xslt.xsl',
    'https://gitlab.coko.foundation/XSweet/HTMLevator/raw/master/applications/header-promote/outline-headers.xsl',
    'https://gitlab.coko.foundation/XSweet/HTMLevator/raw/master/applications/header-promote/digest-paragraphs.xsl',
    'https://gitlab.coko.foundation/XSweet/HTMLevator/raw/master/applications/header-promote/make-header-escalator-xslt.xsl',
    'https://gitlab.coko.foundation/XSweet/XSweet/raw/master/applications/html-polish/final-rinse.xsl',
    'https://gitlab.coko.foundation/XSweet/editoria_typescript/raw/master/editoria-tune.xsl',
    'https://gitlab.coko.foundation/XSweet/editoria_typescript/raw/master/p-split-around-br.xsl',
    'https://gitlab.coko.foundation/XSweet/editoria_typescript/raw/master/editoria-notes.xsl',
    'https://gitlab.coko.foundation/XSweet/editoria_typescript/raw/master/editoria-basic.xsl',
    'https://gitlab.coko.foundation/XSweet/editoria_typescript/raw/master/editoria-reduce.xsl'
];

$outputDir = '/var/www/html/xsl';
if (!is_dir($outputDir) && !mkdir($outputDir, 0755, true)) {
    exit("Could not create $outputDir.\n");
}

foreach ($urls as $url) {
    $input = @fopen($url, 'rb');
    if (!$input) exit("Failed opening $url.\n");
    $outputPath = $outputDir . '/' . basename($url);
    $output = @fopen($outputPath, 'wb');
    if (!$output) exit("Failed opening $outputPath.\n");
    print("Copying $url to $outputPath\n");
    $bytes = stream_copy_to_stream($input, $output);
    fclose($input);
    fclose($output);
    if ($bytes === false || $bytes === 0) exit("Failed copying $url.\n");
}

