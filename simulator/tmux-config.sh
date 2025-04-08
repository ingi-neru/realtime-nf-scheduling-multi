
#!/bin/bash

# Create a new detached tmux session
tmux new-session -d -s "rt multiswitch" -n "codebase"

# Create additional windows
tmux new-window -t "rt multiswitch:" -n "simulation"
tmux new-window -t "rt multiswitch:" -n "results"
tmux new-window -t "rt multiswitch:" -n "git"

# Split the simulation window into 3 panes (optional)
tmux split-window -h -t "rt multiswitch:1"

tmux send-keys -t "rt multiswitch:3" "lazygit" C-m 
tmux send-keys -t "rt multiswitch:0" "nvim ." C-m
tmux send-keys -t "rt multiswitch:2" "cd results && timg -p kitty results.png" C-m
# Optional: Send startup commands to specific panes/windows
# Example: Start htop in simulation pane 2.2
# tmux send-keys -t "rt multiswitch:2.2" "htop" C-m

# Attach to the session
tmux attach -t "rt multiswitch"
