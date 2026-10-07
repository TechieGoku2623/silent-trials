#!/usr/bin/env bash
set +e
silent-trials match --nct NCT00000005 --explain
exit $?
