from nicegui import ui

ui.label('Club Strive Prototype')

ui.button(
    'Kickoff',
    on_click=lambda: ui.notify('Match simulation coming soon')
)

ui.run(host='0.0.0.0', port=8080)
