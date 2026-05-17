# Demonstrates `tesserae project setup` from a fresh project directory.
# Renders to docs/screencasts/setup.gif. Run with: vhs docs/screencasts/setup.tape
#
# Records against /tmp/tesserae-demo-rec/myproject which is a fresh copy of
# examples/demo-corpus/data/research/ (50 papers, 24 repo pages, 11
# synthesis pages). Re-create with:
#
#     rm -rf /tmp/tesserae-demo-rec && mkdir -p /tmp/tesserae-demo-rec/myproject
#     cp -R examples/demo-corpus/data/research /tmp/tesserae-demo-rec/myproject/

Output "docs/screencasts/setup.gif"

Set FontSize 14
Set Width 1100
Set Height 440
Set Theme "Catppuccin Mocha"
Set TypingSpeed 50ms

Type "source /tmp/tesserae-demo-rec/venv/bin/activate"
Enter
Sleep 200ms
Type "cd /tmp/tesserae-demo-rec/myproject && clear"
Enter
Sleep 500ms

Type "# A research notes directory we want to wiki-ify"
Sleep 500ms
Enter

Type "ls research/"
Enter
Sleep 1500ms

Type "# Bootstrap the project: one command, non-interactive"
Sleep 700ms
Enter

Type@30ms "tesserae project setup --yes --source ./research --with-understand-anything --with-raganything --skip-install-cognee --skip-install-raganything --skip-install-understand-anything"
Sleep 500ms
Enter
Sleep 4s

Type "ls .tesserae/"
Enter
Sleep 2500ms
