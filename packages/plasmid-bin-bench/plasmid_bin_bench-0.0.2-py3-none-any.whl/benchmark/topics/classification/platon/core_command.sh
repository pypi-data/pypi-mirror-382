# Environment wrapper script: nothing required

gunzip -k -c "${FASTA_GZ}" >"${GENOME}"

platon "${USER_TOOL_OPTIONS[@]}" --output "${WORK_EXP_SAMPLE_DIR}" "${GENOME}"

rm -rf "${GENOME}"
