"""Tintable HUD symbols, drawn at 64 units for the reference-style panels."""

HUD_ICONS = {
    'helmet': '''<g stroke="white" stroke-width="1.8" stroke-linejoin="round" fill="none">
      <path d="M21 5H27V17H37V5H43L52 13 57 29 55 44 45 58H19L9 44 7 29 12 13Z"/>
      <path d="M21 6 18 19 13 22 12 35 20 42 22 54M43 6l3 13 5 3 1 13-8 7-2 12"/>
      <path d="m15 24 10 4h14l10-4-3 12-8 5H26l-8-5Z"/>
      <path d="m10 38 9 7v6m35-13-9 7v6M26 45h12v10H26Zm4 1v8m4-8v8"/>
      <path d="M14 15h7m22 0h7M21 57l3-4m19 4-3-4"/>
    </g>''',
    'heart': '''<defs><mask id="ecg"><path fill="white" d="M32 16C21 2 5 10 5 24c0 11 14 22 27 33C45 46 59 35 59 24 59 10 43 2 32 16Z"/>
      <path d="M3 30h15l6-10 9 21 6-12h23" fill="none" stroke="black" stroke-width="4" stroke-linejoin="miter"/></mask></defs>
      <path fill="white" mask="url(#ecg)" d="M0 0h64v64H0Z"/>''',
    'steps': '''<defs><mask id="shoe"><path fill="white" d="m15 7 10 8c5 4 9 6 17 7l7 6c6 3 10 10 10 17 0 6-4 9-11 9H11c-5 0-7-3-6-8l2-10 4-8 1-15Z"/>
      <path fill="none" stroke="black" stroke-width="3" stroke-linecap="round" d="m23 18-5 9m13-4-5 8m13-5-4 8M7 44c15 1 34 2 51-1"/>
      </mask></defs><path fill="white" mask="url(#shoe)" d="M0 0h64v64H0Z"/>''',
    'battery': '''<g fill="white"><path fill-rule="evenodd" d="M7 16h45c3 0 4 2 4 5v22c0 3-1 5-4 5H7c-3 0-4-2-4-5V21c0-3 1-5 4-5Zm0 4v24h45V20Z"/>
      <path d="M58 25h4v14h-4ZM11 24h36v16H11Z"/></g>''',
    'runner': '''<g fill="white">
      <circle cx="40" cy="9" r="6"/>
      <path d="M31 18c2-3 6-3 9-1l4 6 6 4 7-6 4 4-9 10c-2 1-4 1-6 0l-7-4-4 10-9 1-4-8 5-13Z"/>
      <path d="m29 19-11 4-7 12 5 3 7-10 10-2Zm-4 19 10 4-9 11-14 2-5 7-5-3 7-11 12-2Zm10 0 10 9-1 11 7 2-1 4H38l-1-13-10-7Z"/>
    </g>''',
    'radar': '''<path d="M32 32 14 10A28 28 0 0 1 56 18Z" fill="white" opacity=".16"/>
      <g stroke="white" stroke-width="1.2" fill="none" opacity=".85">
      <circle cx="32" cy="32" r="28"/><circle cx="32" cy="32" r="19"/>
      <circle cx="32" cy="32" r="10"/><path d="M32 3v58M3 32h58m29 0L14 10"/></g>
      <circle cx="32" cy="32" r="3.6" fill="white"/>
      <circle cx="39" cy="17" r="2.2" fill="white" opacity=".9"/>''',
    'target': '''<g stroke="white" stroke-width="2" fill="none">
      <path d="M11 22a23 23 0 0 1 42 0M11 42a23 23 0 0 0 42 0M22 11a23 23 0 0 0 0 42M42 11a23 23 0 0 1 0 42"/>
      <circle cx="32" cy="32" r="15"/><path d="M32 4v14m0 28v14M4 32h14m28 0h14"/>
      </g><circle cx="32" cy="32" r="3" fill="white"/>''',
    'telemetry': '''<g fill="white"><path d="M10 8h44v4H10Zm0 9h35v4H10Zm0 9h44v4H10Zm0 9h30v4H10Zm0 9h44v4H10Zm0 9h26v4H10Z"/></g>''',
}
