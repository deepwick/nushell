# Deepwick for Nushell. Source this file from config.nu.

$env.config.color_config = {
    separator: '#6E7899'
    leading_trailing_space_bg: { attr: n }
    header: { fg: '#569CD6' attr: b }
    empty: '#6E7899'
    bool: '#569CD6'
    int: '#B5CEA8'
    float: '#B5CEA8'
    filesize: '#B5CEA8'
    duration: '#B5CEA8'
    datetime: '#7A86A8'
    range: '#D4D4D4'
    string: '#D4D4D4'
    glob: '#D4D4D4'
    nothing: '#6E7899'
    binary: '#B5CEA8'
    cell-path: '#9CDCFE'
    row_index: '#6E7899'
    record: '#D4D4D4'
    list: '#D4D4D4'
    closure: '#D4D4D4'
    block: '#D4D4D4'
    custom: '#D4D4D4'
    hints: '#6E7899'
    search_result: { fg: '#D7BA7D' bg: '#264F78' }
    banner_foreground: '#D4D4D4'
    banner_highlight1: '#569CD6'
    banner_highlight2: '#C586C0'
    binary_null_char: '#6E7899'
    binary_printable: '#D4D4D4'
    binary_whitespace: '#6E7899'
    binary_ascii_other: '#C586C0'
    binary_non_ascii: '#D7BA7D'
    shape_binary: '#B5CEA8'
    shape_block: '#D4D4D4'
    shape_bool: '#569CD6'
    shape_closure: '#D4D4D4'
    shape_custom: '#D4D4D4'
    shape_datetime: '#B5CEA8'
    shape_directory: { fg: '#D4D4D4' attr: u }
    shape_external: '#DCDCAA'
    shape_external_resolved: '#DCDCAA'
    shape_externalarg: '#D4D4D4'
    shape_filepath: { fg: '#D4D4D4' attr: u }
    shape_flag: '#9CDCFE'
    shape_float: '#B5CEA8'
    shape_garbage: { fg: '#F44747' attr: u }
    shape_glob_interpolation: { fg: '#D4D4D4' attr: u }
    shape_globpattern: { fg: '#D4D4D4' attr: u }
    shape_int: '#B5CEA8'
    shape_internalcall: '#DCDCAA'
    shape_keyword: '#569CD6'
    shape_list: '#D4D4D4'
    shape_literal: '#D4D4D4'
    shape_match_pattern: '#D4D4D4'
    shape_matching_brackets: { attr: u }
    shape_nothing: '#569CD6'
    shape_operator: '#D4D4D4'
    shape_pipe: '#D4D4D4'
    shape_range: '#D4D4D4'
    shape_raw_string: '#CE9178'
    shape_record: '#D4D4D4'
    shape_redirection: '#D4D4D4'
    shape_signature: '#4EC9B0'
    shape_string: '#CE9178'
    shape_string_interpolation: '#CE9178'
    shape_table: '#D4D4D4'
    shape_vardecl: '#9CDCFE'
    shape_variable: '#9CDCFE'
}

const DEEPWICK_MENU_STYLE = {
    text: '#D4D4D4'
    selected_text: { fg: '#D4D4D4' bg: '#264F78' attr: b }
    description_text: { fg: '#7A86A8' attr: i }
    match_text: { fg: '#DCDCAA' attr: u }
    selected_match_text: { fg: '#DCDCAA' bg: '#264F78' attr: b }
}

const DEEPWICK_DEFAULT_MENUS = [
    { name: completion_menu only_buffer_difference: false marker: "| "
      type: { layout: columnar columns: 4 col_width: 20 col_padding: 2 tab_traversal: "horizontal" } }
    { name: ide_completion_menu only_buffer_difference: false marker: "| "
      type: { layout: ide min_completion_width: 0 max_completion_width: 50 max_completion_height: 10
              padding: 0 border: true cursor_offset: 0 description_mode: "prefer_right"
              min_description_width: 15 max_description_width: 50 max_description_height: 10
              description_offset: 1 correct_cursor_pos: false } }
    { name: history_menu only_buffer_difference: true marker: "? "
      type: { layout: list page_size: 10 } }
    { name: help_menu only_buffer_difference: true marker: "? "
      type: { layout: description columns: 4 col_width: 20 col_padding: 2 selection_rows: 4
              description_rows: 15 } }
]

$env.config.menus = do {
    let existing = $env.config.menus | each {|m| $m.name }
    let restyled = $env.config.menus | each {|m|
        if $m.name in ($DEEPWICK_DEFAULT_MENUS | get name) {
            $m | upsert style (($m.style? | default {}) | merge $DEEPWICK_MENU_STYLE)
        } else { $m }
    }
    let added = $DEEPWICK_DEFAULT_MENUS
        | where {|d| $d.name not-in $existing }
        | each {|d| $d | insert style $DEEPWICK_MENU_STYLE }
    $restyled ++ $added
}
