# TaxEval

In this repo you'll find some evals for LLMs for tax questions. Here are the results as of today:

|    | Model                     | Score   |
|---:|:--------------------------|:--------|
|  1 | openai/gpt-4-1106-preview | 56.9%   |
|  2 | anthropic/claude-2        | 42.6%   |
|  3 | openai/gpt-3.5-turbo-1106 | 40.7%   |
|  4 | replicate/mistral-7b      | 30.6%   |


## Running this eval
1. Place your Anthropic, OpenAI, and Replicate API keys in your .env file, or in ~/.env. 
2. Run `python main.py`.
3. `llm.py` contains some nice code for asking multiple LLMs several questions at once.

## FAQ
Q: What about thinking step-by-step?

A: That's a good idea. This was a first test at zero-shot reasoning. I'm sure there are ways to improve it.

Q: How stable were the results?

A: This merits deeper investigation, but in the situations where everyone got the answer wrong, it is fairly unstable. It would be good to re-run the suite and test for that.

Q: Why didn't you zero the temperature?

A: I used the default settings for each model because I sort of assume that's the most fair test. If you have better ideas, please submit a PR! 

Q: I am an accountant and I noticed horrific factual errors in the test suite.

A: Huh! I expected as much... please submit a pull request, thank you!


## Examples
#### Question 12
On January 31, Year 2, Beau Corp. issued $300,000 maturity value, 12% bonds for $300,000 cash. The bonds are dated December 31, Year 1, and mature on December 31, Year 11. Interest will be paid semi-annually on June 30 and December 31. What amount of accrued interest payable should Beau report in its September 30, year 2 balance sheet?
1. $27,000
2. $24,000
3. $18,000
4. $9,000


replicate/mistral-7b: "3. $18,000" (3) ❌  
openai/gpt-3.5-turbo-1106: "3" (3) ❌  
openai/gpt-4-1106-preview: "4" (4) ✅  
anthropic/claude-2: " 3. $18,000" (3) ❌  
Correct: 4

#### Question 29
When purchasing a bond, the present value of the bond's expected net future cash inflows discounted at the market rate of interest provides what information about the bond?
1. Price
2. Par
3. Yield
4. Interest


replicate/mistral-7b: "1. Price" (1) ✅  
openai/gpt-3.5-turbo-1106: "3" (3) ❌  
openai/gpt-4-1106-preview: "1" (1) ✅  
anthropic/claude-2: " 1" (1) ✅  
Correct: 1


#### Question 39
If a city government is the primary reporting entity, which of the following is an acceptable method to present component units in its combined financial statements?
1. Consolidation
2. Cost method
3. Discrete presentation
4. Government-wide presentation


replicate/mistral-7b: "1. Consolidation" (1) ❌  
openai/gpt-3.5-turbo-1106: "2" (2) ❌  
openai/gpt-4-1106-preview: "3" (3) ✅  
anthropic/claude-2: " 3. Discrete present" (3) ✅  
Correct: 3  

#### Question 97
On April 1, Aloe, Inc. factored $80,000 of its accounts receivable without recourse. The factor retained 10% of the accounts receivable as an allowance for sales returns and charged a 5% commission on the gross amount of the factored receivables. What amount of cash did Aloe receive from the factored receivables?
1. $68,000
2. $68,400
3. $72,000
4. $76,000


replicate/mistral-7b: "1. $68,000" (1) ✅  
openai/gpt-3.5-turbo-1106: "4" (4) ❌  
openai/gpt-4-1106-preview: "2" (2) ❌  
anthropic/claude-2: " 2. $68,400" (2) ❌  
Correct: 1

