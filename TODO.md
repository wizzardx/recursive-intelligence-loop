# TODO

## High Priority
- [ ] Add robust error handling
  - [ ] API calls (rate limits, timeouts)
  - [ ] Retry logic for failed API calls
  - [ ] File operations
  - [ ] XML parsing errors

- [ ] Improve configuration management
  - [ ] Move hardcoded values to config file
  - [ ] Add environment variable support with defaults
  - [ ] Support command-line argument overrides

## Medium Priority
- [ ] Enhance chat session management
  - [ ] Add delete/archive functionality
  - [ ] Implement chat search
  - [ ] Add chat metadata (tags, descriptions)
  - [ ] Support chat export/import

- [ ] Improve code structure
  - [ ] Split into modules (config, api, chat, ui)
  - [ ] Replace print statements with proper logging
  - [ ] Add comprehensive type hints
  - [ ] Implement unit tests

## Future Features
- [ ] UI/UX improvements
  - [ ] Progress indicators for API calls
  - [ ] Better chat selection interface
  - [ ] Preview chat history without loading
  - [ ] Command-line flags for operation modes

- [ ] Advanced features
  - [ ] Support multiple models/providers
  - [ ] Chat summaries
  - [ ] Conversation branching
  - [ ] Conversation merging
  - [ ] Alternative output formats

## Nice to Have
- [ ] Documentation improvements
  - [ ] Add API documentation
  - [ ] Add usage examples
  - [ ] Add architecture overview
  - [ ] Add contribution guidelines

## Done
- [x] Initial implementation
- [x] Basic chat logging
- [x] XML/MD storage format
- [x] Chat resume functionality
