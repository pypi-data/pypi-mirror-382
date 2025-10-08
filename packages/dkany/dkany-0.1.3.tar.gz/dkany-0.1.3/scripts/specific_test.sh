rm -rf test-reports/*

uv run python -m pytest \
    --cov functions \
    --cov-report html:./test-reports/cov \
    --cov-report xml:./test-reports/cov.xml \
    ./tests/test_compare_output.py \
    --html=./test-reports/test.html \
    --junitxml=./test-reports/test.xml