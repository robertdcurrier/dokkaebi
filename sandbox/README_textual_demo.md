# Textual DOS Demo - Clean & Simple

## What It Is
A bulletproof, working foundation for DOS-style Textual applications. No fancy features, just solid, tested functionality.

## Features
- **DOS Menu Bar**: File, Edit, View, etc. at the top
- **Function Key Bar**: F1=Help, F2=Save, etc. at the bottom  
- **Two Scrollable Windows**: Left (Lorem Ipsum) and Right (Numbered Data)
- **Classic DOS Styling**: Blue background (#0000AA), white text, thick borders
- **Proper Keyboard Navigation**: Tab, arrow keys, Page Up/Down all work

## How to Run
```bash
cd /Users/rdc/src/dokkaebi
python sandbox/textual_demo_clean.py
```

## Controls
- **Tab**: Switch between left and right windows
- **Arrow Keys**: Scroll within focused window
- **Page Up/Down**: Fast scroll within focused window  
- **F1**: Help (beeps in demo)
- **F10 or Q or Escape**: Quit the application

## What Makes It Bulletproof
1. **Uses ONLY documented Textual widgets** - No experimental features
2. **Follows memory bank best practices** - Proper widget IDs, CSS structure
3. **Independent scrolling** - Each window scrolls separately with built-in functionality
4. **Classic DOS appearance** - Authentic blue/white color scheme with borders
5. **Proper error handling** - Imports tested, no runtime failures

## The Code Structure
- `DOSMenuBar`: Static menu at top
- `DOSFunctionKeyBar`: Static function keys at bottom
- `ScrollableTextWindow`: Reusable scrollable content container
- `DOSDemo`: Main app class with proper CSS and keyboard bindings

## Perfect Foundation For
- File managers
- Text editors  
- Data viewers
- Configuration tools
- Any DOS-style business application

## Tested and Working
✅ Imports successfully  
✅ Runs without errors  
✅ Displays proper DOS styling  
✅ Both windows scroll independently  
✅ Keyboard navigation works  
✅ Focus switching with Tab works  

This is a WORKING demo you can run immediately and build upon.