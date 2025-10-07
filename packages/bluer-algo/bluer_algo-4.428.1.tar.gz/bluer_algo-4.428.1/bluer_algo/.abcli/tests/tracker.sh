#! /usr/bin/env bash

function test_bluer_algo_tracker() {
    local options=$1

    local object_name

    bluer_ai_eval ,$options \
        bluer_algo_tracker \
        algo=void,$options
    [[ $? -eq 0 ]] && return 1
    bluer_ai_hr

    object_name=test_bluer_algo_tracker-$(bluer_ai_string_timestamp)
    bluer_ai_eval ,$options \
        bluer_algo_tracker \
        algo=camshift,$options \
        $object_name \
        --frame_count 5 \
        --log 1 \
        --show_gui 0 \
        --verbose 1
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    object_name=test_bluer_algo_tracker-$(bluer_ai_string_timestamp)
    bluer_ai_eval ,$options \
        bluer_algo_tracker \
        algo=camshift,$options \
        $object_name \
        --frame_count 5 \
        --log 0 \
        --show_gui 0 \
        --verbose 1
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    object_name=test_bluer_algo_tracker-$(bluer_ai_string_timestamp)
    bluer_ai_eval ,$options \
        bluer_algo_tracker \
        algo=meanshift,$options \
        $object_name \
        --frame_count 5 \
        --log 1 \
        --show_gui 0 \
        --verbose 1
    [[ $? -ne 0 ]] && return 1
    bluer_ai_hr

    object_name=test_bluer_algo_tracker-$(bluer_ai_string_timestamp)
    bluer_ai_eval ,$options \
        bluer_algo_tracker \
        algo=meanshift,$options \
        $object_name \
        --frame_count 5 \
        --log 0 \
        --show_gui 0 \
        --verbose 1
}
