# To-Do Project Requirement

## Task Checklist
- [x] Review the project brief and define the user-facing requirements for the to-do list app.
- [x] Set up a Flask-based web app structure that serves the task list on the home page.
- [x] Create a task form with title and optional due date entry.
- [x] Add support for creating, editing, deleting, and toggling task completion states.
- [x] Add filters for all, active, and completed tasks.
- [x] Save task data between refreshes using a local JSON file so the list persists in the browser environment.
- [x] Style the interface to match the design brief: clean layout, responsive behavior, graphic header, and watermark text “Oh no!”.
- [x] Validate the app with focused tests and a local Flask development run.

## Business Requirements
Create a simple to-do list application that helps users organize tasks, track due dates, and quickly update progress without a complex interface.

## User Requirements
- Users can add a task with a title and optional due date.
- Users can edit an existing task.
- Users can delete tasks.
- Users can mark tasks as completed or active.
- Completed tasks are visually distinct from active tasks.
- Users can filter tasks by all, active, or completed state.
- Tasks remain available after refreshes by persisting them in local app storage.
- The app works on desktop and mobile screens.
- The interface stays clean and easy to use.
- The page has decorative top graphics and a watermark reading “Oh no!”.

## Software Requirements
- Python 3
- Flask
- HTML and CSS
- No JavaScript required for the task interactions
- Keep a development trace in a Markdown file for reproducibility and review

## Notes
This implementation stores tasks in a local JSON file so the list persists between refreshes without introducing JavaScript.
