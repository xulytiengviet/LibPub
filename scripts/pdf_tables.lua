-- Give every table an explicit total width so Pandoc/XeLaTeX wraps cells
-- inside the printable area instead of allowing long content to clip.
function Table(table_block)
  local column_count = #table_block.colspecs
  if column_count == 0 then
    return table_block
  end
  local printable_fraction = 0.94
  local column_width = printable_fraction / column_count
  for index, spec in ipairs(table_block.colspecs) do
    spec[2] = column_width
    table_block.colspecs[index] = spec
  end
  return table_block
end
