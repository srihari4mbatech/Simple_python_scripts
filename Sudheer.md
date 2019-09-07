## Sudheer Questions:

#### Here are the questions: 

Please provide as complete answers as possible with examples of software, packages, written code and proxy data.  the code has to be executable, if we insert it in R/Python and run through it should provide output that you refer to. For the coding question, please explain the task the current R code is doing and translate that to Python syntax, you can assume that I’ll have all the variables that I have in R environment, but functions need to come from Python.

Any code provided needs to be run through – once open in R studio or Python it needs to install needed packages, connect (the testing machine will be online though Dell VPN) and run the procedures.

Due date – midnight CST US Sun (Sun evening)

Have fun!
Anna

1. You have a time series of revenue from a particular sport gear store. It is time series with weeks assigned. The time series have seasonality and trend. The goal is to predict the next  10 weeks as accurately as possible. The data is attached in Excel file, please use software that you see fit and provide the code together with your answers. The code has to be run through, that means if I open in R environment I should be able to run end to end and have the forecast in the output. The white paper should have explanation of model selection and the criteria of the choice of the model and parameters if needed.

2. You want to find what are the physical addresses for your customer base. You have a list of 200k customers, their names and country. You need to find their actual locations/addresses with all the details including street / state / zip code / etc. One of the sources of information can be company websites, you can think of any other source – please provide examples. Please provide a framework how you would approach that task and what would be the apps, tools, packages you’d use. How would you automate web scrapping if you need to expand your list of customers to 5M. what are the caveats?  Bonus – create a sample for a small set of customers (~2-5 random companies of your choice) to illustrate how the concept will work.

3. Please re-write the following code in Python:

``` R
        tmp <- ddply(filter(master_subset, SNPSH_DT == CLSD_DT &

                    SNPSH_DT != 0 &

                    SNPSH_DT < (TT+1)),  ~ SNPSH_DT, function(x) {

                        x[is.na(x$DEAL_SIZE)==TRUE]=0;

                        sum(x$DEAL_SIZE,na.rm=TRUE)

                    })
```

4. Please explain what are the benefits of Deep learning and how it differentiates from GLM, Decision trees class of models?

5. Please provide an example of a web scrapping techniques when you had to overcome challenges (blocking, time outs, reverse API changes). If you didn’t have that experience firsthand feel free to provide recommendations to a few examples you’ve known/seen

6. You have a code written in R that runs StepWise linear regression, random forest, and xgboost on 500k rows. Computational time of your code takes ~10 hours. you need to scale your algorithm to 20M rows. What would be your steps to manage the task in meaningful way, please make assumptions about the data and the process you are modelling to answer that question. What equipment / support you’ll  need (please be specific about Hardware specifications or virtual machine designations).

7. You need to evaluate mapping of company names between the two lists, each list has name (with typos and not always in a standardized format), address (most of the accounts but not all have addresses: country/city/street address/zip code, order of the entries are not always the same, city can be coming after country, some US companies have States, some UK companies have provinces, etc.), some accounts also have URL addresses. Please describe the steps you’ll need to accomplish to clean the two lists data and to map the two lists. Please be explicit about the software/packages you’ll be using.

  

  