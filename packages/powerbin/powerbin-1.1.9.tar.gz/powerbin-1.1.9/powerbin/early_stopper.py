"""
#####################################################################

Copyright (C) 2025 Michele Cappellari  
E-mail: michele.cappellari_at_physics.ox.ac.uk  

Updated versions of this software are available at:  
https://pypi.org/project/powerbin/  

If you use this software in published research, please acknowledge it as:  
“PowerBin method by Cappellari (2025, MNRAS submitted)”  
https://arxiv.org/abs/2509.06903  

This software is provided “as is”, without any warranty of any kind,  
express or implied.  

Permission is granted for:  
 - Non-commercial use.  
 - Modification for personal or internal use, provided that this  
   copyright notice and disclaimer remain intact and unaltered  
   at the beginning of the file.  

All other rights are reserved. Redistribution of the code, in whole or in part,  
is strictly prohibited without prior written permission from the author.  

#####################################################################

V1.0.0: PowerBin created — MC, Oxford, 10 September 2025

Vx.x.xx: Additional changes are documented in the global CHANGELOG.rst
    file of the PowerBin package
"""

#-----------------------------------------------------------------------

class EarlyStopper:
    """
    Stops an optimization process when the best recorded value barely 
    improves over a rolling window of iterations.
    """
    def __init__(self, window=20, min_iters=30, rel_tol=0.05, abs_tol=0.05):

        self.window = window
        self.rel_tol = rel_tol
        self.min_iters = min_iters
        self.abs_tol = abs_tol
        self.best_history = [float('inf')]
        self.iter = 0
        self.last = float('inf')
        self.under_relax = False   # Used by the calling function

#-----------------------------------------------------------------------

    def update(self, value: float) -> bool:
        """Feeds the next scalar measurement (`value`)."""

        self.iter += 1

        if value > self.last:
            self.under_relax = True  # latch on first increase
        self.last = value

        # 1. Update running best
        current_best = min(value, self.best_history[-1])
        self.best_history.append(current_best)

        # 2. Skip check if not enough iterations have passed
        if self.iter < max(self.min_iters, self.window):
            return False

        # 3. Get values for comparison (look back `window` steps)
        best_then = self.best_history[-self.window - 1]
        best_now = self.best_history[-1]

        # 4. Check if improvement is sufficient to continue
        threshold = max(self.abs_tol, self.rel_tol * abs(best_then))
        if best_then - best_now > threshold:
            return False  # Continue, improvement is sufficient

        return True
    
#-----------------------------------------------------------------------