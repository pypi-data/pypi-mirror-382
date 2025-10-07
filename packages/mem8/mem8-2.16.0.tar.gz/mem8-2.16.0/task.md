Check notes inline on UX / experience questions:

-----

🤖 Claude Code project detected

Detected: python project

Template options: full, claude-config, thoughts-repo (or 'none' to skip templates)
Template type [full]: claude-config
##  Can we please provide a typer / rich interface that allows for a user to use arrow-keys to choose selections like here and other areas below?


📋 Template Configuration
Workflow options: github, linear, none
Workflow provider (GitHub is free and open source) [github]: 
## Ensure that this option is tied to the inclusion of the proper commands and removal of the other installed commands (linear vs github issues) and that this is persisted somewhere like in ~/.mem8 type of file like kubectl does

Automation options: standard, advanced, none
Workflow automation level [standard]: 
## It is completely unclear what this is for, if it is not used or clear, please remove this or properly document it and explain the choice to the user here clearly

GitHub organization/username [your-org]: 
GitHub repository name [your-repo]: 
## be clear that the format that you want the info about org / username and repository name as well if gh client is installed you can perhaps glean some of this and pre-fill it - we want to make this super eassy for those already ussing gh cli and or already have a GH_TOKEN in the env to work with for private repos etc - should be super easy.

If we have to we can setup an oauth flow or use anything in the github sdk or cli that works well and smoothly here.

