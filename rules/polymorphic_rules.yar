rule high_entropy_pattern {
    meta:
        description = "Heuristic: binary with high entropy-like byte sequences"
    strings:
        $a = /\x00\x??\x00/ nocase
    condition:
        filesize > 0
}

rule suspicious_api_strings {
    meta:
        description = "Contains suspicious API strings often used in injection"
    strings:
        $valloc = "VirtualAlloc"
        $vprot = "VirtualProtect"
        $crthread = "CreateRemoteThread"
    condition:
        any of them
}
