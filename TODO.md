# TODOs

- Make demo Videos: playground switching sys prompts, transfer sys prompt to custom model with docs
- Models and docs need ownership and visibility in database, owner str, visibility [str]
- Ability to share docs/models by pasting an email of another user ("This email is belongs to a sandbox user. They will now have access to the model" / "This email does not belong to a sandbox user"). Probably want comma separation...
- Add http links to Doc upload options
- Fix tagging ux, add tags should be clickable, should save when you hit save
- Check and batch-tag multiple docs
- documents tab needs a spinner when processing docs
- existing tags should be selectable when adding to docs
- Need initial (Type a message down there 👇 to get started / explain that this is a chat interface) message for new users
- Soft outline around new chat and documents buttons
- Fix translations for docs & more and search your chats, as well as sign in screen
- create a couple default custom prompts shortcuts like /quick-summary ([type something here]) and /quick-summary-from-paste {{clipboard}}
- Unhide Tools from Docs & more layout
- Chroma is kept in ram... need to swap for redisVL
