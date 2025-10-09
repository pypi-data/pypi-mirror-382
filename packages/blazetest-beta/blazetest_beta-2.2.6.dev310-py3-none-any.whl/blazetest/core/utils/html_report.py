"""
Simple HTML report generator for BlazeTest.
Converts JUnit XML to a clean, styled HTML report.
"""

import logging
from datetime import datetime
from junitparser import JUnitXml

logger = logging.getLogger(__name__)


def generate_html_report(junit_xml: JUnitXml, title: str = "BlazeTest Report") -> str:
    """
    Generate a clean HTML report from JUnit XML.

    Args:
        junit_xml: Parsed JUnit XML object
        title: Report title

    Returns:
        str: Complete HTML document
    """
    # Collect statistics
    total_tests = 0
    passed = 0
    failed = 0
    skipped = 0
    errors = 0
    total_time = 0.0
    test_cases = []

    for suite in junit_xml:
        for case in suite:
            total_tests += 1
            test_time = float(case.time) if case.time else 0.0
            total_time += test_time

            # Determine status
            status = "passed"
            status_class = "status-pass"
            message = ""

            if case.is_skipped:
                skipped += 1
                status = "skipped"
                status_class = "status-skip"
                if hasattr(case, "skipped") and case.skipped:
                    message = case.skipped.message or ""
            elif case.result:
                # Has failure or error
                if hasattr(case.result[0], "__class__"):
                    result_type = case.result[0].__class__.__name__
                    if result_type == "Error":
                        errors += 1
                        status = "error"
                        status_class = "status-error"
                    else:
                        failed += 1
                        status = "failed"
                        status_class = "status-fail"
                    message = (
                        case.result[0].message
                        if hasattr(case.result[0], "message")
                        else str(case.result[0])
                    )
            else:
                passed += 1

            test_cases.append(
                {
                    "classname": case.classname or "",
                    "name": case.name or "",
                    "time": test_time,
                    "status": status,
                    "status_class": status_class,
                    "message": message,
                }
            )

    # Calculate pass rate
    pass_rate = (passed / total_tests * 100) if total_tests > 0 else 0

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        
        .header .timestamp {{
            opacity: 0.9;
            font-size: 0.9em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-card.total .number {{ color: #667eea; }}
        .stat-card.pass .number {{ color: #28a745; }}
        .stat-card.fail .number {{ color: #dc3545; }}
        .stat-card.skip .number {{ color: #ffc107; }}
        .stat-card.error .number {{ color: #fd7e14; }}
        .stat-card.rate .number {{ color: #667eea; }}
        .stat-card.time .number {{ color: #17a2b8; }}
        
        .progress-bar {{
            margin: 0 40px 40px;
            height: 40px;
            background: #e9ecef;
            border-radius: 20px;
            overflow: hidden;
            display: flex;
        }}
        
        .progress-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
            transition: all 0.3s;
        }}
        
        .progress-segment:hover {{
            filter: brightness(1.1);
        }}
        
        .progress-pass {{ background: #28a745; }}
        .progress-fail {{ background: #dc3545; }}
        .progress-skip {{ background: #ffc107; }}
        .progress-error {{ background: #fd7e14; }}
        
        .tests-section {{
            padding: 40px;
        }}
        
        .tests-section h2 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.8em;
        }}
        
        .filter-buttons {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .filter-btn:hover {{
            background: #667eea;
            color: white;
        }}
        
        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .test-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        
        .test-item {{
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            transition: all 0.2s;
        }}
        
        .test-item:hover {{
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            border-color: #667eea;
        }}
        
        .test-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .test-name {{
            font-weight: 600;
            color: #333;
            font-size: 1.1em;
        }}
        
        .test-class {{
            color: #6c757d;
            font-size: 0.85em;
            margin-bottom: 8px;
        }}
        
        .test-meta {{
            display: flex;
            align-items: center;
            gap: 15px;
            font-size: 0.9em;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-pass {{
            background: #d4edda;
            color: #155724;
        }}
        
        .status-fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .status-skip {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .status-error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .test-time {{
            color: #6c757d;
        }}
        
        .test-message {{
            margin-top: 12px;
            padding: 12px;
            background: #f8f9fa;
            border-left: 4px solid #dc3545;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #333;
            white-space: pre-wrap;
            word-break: break-word;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .footer strong {{
            color: #667eea;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .test-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 {title}</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card total">
                <div class="number">{total_tests}</div>
                <div class="label">Total Tests</div>
            </div>
            <div class="stat-card pass">
                <div class="number">{passed}</div>
                <div class="label">Passed</div>
            </div>
            <div class="stat-card fail">
                <div class="number">{failed}</div>
                <div class="label">Failed</div>
            </div>
            <div class="stat-card skip">
                <div class="number">{skipped}</div>
                <div class="label">Skipped</div>
            </div>
            <div class="stat-card error">
                <div class="number">{errors}</div>
                <div class="label">Errors</div>
            </div>
            <div class="stat-card rate">
                <div class="number">{pass_rate:.1f}%</div>
                <div class="label">Pass Rate</div>
            </div>
            <div class="stat-card time">
                <div class="number">{total_time:.1f}s</div>
                <div class="label">Duration</div>
            </div>
        </div>
        
        <div class="progress-bar">
"""

    # Add progress bar segments
    if passed > 0:
        pass_width = passed / total_tests * 100
        html += f'            <div class="progress-segment progress-pass" style="width: {pass_width}%">{passed} Passed</div>\n'

    if failed > 0:
        fail_width = failed / total_tests * 100
        html += f'            <div class="progress-segment progress-fail" style="width: {fail_width}%">{failed} Failed</div>\n'

    if skipped > 0:
        skip_width = skipped / total_tests * 100
        html += f'            <div class="progress-segment progress-skip" style="width: {skip_width}%">{skipped} Skipped</div>\n'

    if errors > 0:
        error_width = errors / total_tests * 100
        html += f'            <div class="progress-segment progress-error" style="width: {error_width}%">{errors} Errors</div>\n'

    html += """        </div>
        
        <div class="tests-section">
            <h2>Test Results</h2>
            
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterTests('all')">All ({total_tests})</button>
                <button class="filter-btn" onclick="filterTests('passed')">Passed ({passed})</button>
                <button class="filter-btn" onclick="filterTests('failed')">Failed ({failed})</button>
                <button class="filter-btn" onclick="filterTests('skipped')">Skipped ({skipped})</button>
                <button class="filter-btn" onclick="filterTests('error')">Errors ({errors})</button>
            </div>
            
            <div class="test-list" id="test-list">
""".format(
        total_tests=total_tests,
        passed=passed,
        failed=failed,
        skipped=skipped,
        errors=errors,
    )

    # Add test cases
    for test in test_cases:
        message_html = ""
        if test["message"]:
            # Escape HTML and limit message length
            escaped_message = test["message"].replace("<", "&lt;").replace(">", "&gt;")
            if len(escaped_message) > 500:
                escaped_message = escaped_message[:500] + "..."
            message_html = f'<div class="test-message">{escaped_message}</div>'

        html += f"""                <div class="test-item" data-status="{test['status']}">
                    <div class="test-header">
                        <div>
                            <div class="test-name">{test['name']}</div>
                            <div class="test-class">{test['classname']}</div>
                        </div>
                        <div class="test-meta">
                            <span class="test-status {test['status_class']}">{test['status']}</span>
                            <span class="test-time">⏱️ {test['time']:.2f}s</span>
                        </div>
                    </div>
                    {message_html}
                </div>
"""

    html += """            </div>
        </div>
        
        <div class="footer">
            Generated by <strong>BlazeTest</strong> - Parallel Testing on AWS Lambda
        </div>
    </div>
    
    <script>
        function filterTests(status) {
            const testItems = document.querySelectorAll('.test-item');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Update active button
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Filter tests
            testItems.forEach(item => {
                if (status === 'all') {
                    item.style.display = 'block';
                } else {
                    item.style.display = item.dataset.status === status ? 'block' : 'none';
                }
            });
        }
    </script>
</body>
</html>"""

    return html
