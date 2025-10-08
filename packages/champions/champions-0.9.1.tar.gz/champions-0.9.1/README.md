# Champions 


## Status

Disclaimer Doku muss noch gemahct werden.

## Initial Thoughts

The idea of this project is to make binary classification. It departs from some well-established Machine Learning methods in order to test some new ones. Some are purely technical, while others are more fundamental. This is a complete rewrite of my first private package, which I called Pilze (mushrooms). In German, "Champions" and "Champignons" sound similar, which is why I liked the name. But "Mushrooms" explains the project's purpose very well. Mushrooms are neither plants nor animals, but somewhere in between. In ML, it's all about correlations, and in a very abstract way, neural networks and tree-based algorithms solve this problem in opposite directions. Neural networks look at a single event and try to learn all correlations at one stage, while tree-based ML algorithms look at all (or many) events and try to find the correlations stage by stage. SVMs are a step further than trees, but in my personal opinion, they focus on the wrong thing. They focus on separation and not on the correlation of the individual classes. The initial idea of this project was to build a tree in which nodes not only make one cut but a set of cuts in more than one dimension. When it comes to implementations, the obvious choice is to use sklearn. It is one of the best software projects ever built, in my opinion. But some things are really annoying, and overall, it is hard to fit new ideas into this very strict framework.
