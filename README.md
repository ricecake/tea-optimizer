# Tea Optimizer

Have you ever found yourself making vanilla sugar for tea out of basic checmical inputs, and thought to yourself "Gee, I wonder if I'm using enough ethyl vanillin, or too much vanillin"?

Me too!

That's why I made this tea optimizer, which uses a bayesian optimizer to extimate the correct ratios of input ingredients while making the sugar, as well as the correct proportion of inputs to use while making the tea.

It expects as inputs the blends of different vanilla sugars, the water, sugar blend weight, and almond milk used for brewing the cup.
Then you can annotate the cup with the entirely subjective unitless quality ranking.


Since it gauges the cups based on all ingredients, it does some fun and tricky things to project the recommended quantities of sugar components onto the available blend, which is scaled to be as close to the recommendation as possible.

### Isn't this massively too complicated for a cup of tea?
Yes it is, but I had the data, so I had to do it.

## Sample display
![image](https://github.com/ricecake/tea-optimizer/assets/2078127/594118ac-9fb8-492a-b38f-9867dfe57865)

### Dear lord that's hideous
That's not question, but it's also true.   
I was not interested in making it pretty, but if you have suggestions, feel free.  :) 

### Can it support other things?
Yes, but only if it has the same number of ingredients, and you can remember what the boxes mean, or you want to change the code.

### What type of tea?
Tea.  Earl Grey.  Hot.
