# Excel-but-better Prototype
The idea is harness the power of Python with a good Excel-interop story. We have to provide version control, facilities for more structured processing (I'm thinking building a "formula library" and laying out dataframes in the spreadsheet), etc.

We take a financial (numerically oriented) model and turn it into Python code. We can do this on a cell-by-cell basis. The fundamental facility here is "how far do you follow the dependency graph", i.e. how do you select which cells are going to be your input. You can use a simple list or tree-selector to indicate which inputs you would like, by sort of 'expanding' dependencies.  
This Python code is can then be put in the workbook-namespace with a single press of the button. Detecting duplicate code is relevant here, but you can do that on Excel-formulas (or AST's) by asking if they are equivalent.
We can provide a feature for "automatic refactoring" of formulas which have been "shot across". There's a bit of ugliness with starting values, which can lead to some kind of recursive formulas, but typically the starting values can be applied outside of the range.

The basic view, then, is to have a table-pane and a code pane. The code pane has the variables on top and the generated code on the bottom. On smaller screens the variables-code can take up the whole screen, with the back-action taking back to the cell. The generated code is always functional: all input are taken together. Since Excel is Functional Reactive Programming, this is not such an issue.

The other way around, you can write some Python code in a code pane and get a tabular view back. Adding another line adds another cell (horizontally) and you can then add more lines of data vertically. Here again is some nastiness with dealing with starting values and referencing to previous formula output. Perhaps introduce some formula-navigation shortcuts that can be used to select variables in the Python code.

A good example for the recursive initializer is Fibonacci.

Some open questions:

* How do we test?
    - For now I think exposing Python's `assert` as a function might be good, then just running pytest on the generated unit tests. Thin layer on top of pytest could provide the test runner. We can add some facilities for dropping the user into the right bit of code when a test fails. Or like a click in the report.
    - Thinking about property testing and writing Python from scratch, we might need to get some mock-data generation thing going. Though I'd rather just import hypothesis (which isn't very good for developing)
* How do we deal with recursion and "seed values"?
    - Seed values can be either inline or on top of the column.
* How could we allow use of objects like sklearn models? Also, how do you develop connectors for databases and stuff? Could you do that in the program itself?
    - Potentially you could let the object just live on the sheet some where (I think Apple Tables used to do something like this), but then you want the user to be able to control updating of the sheet cells. Highlighting for not up-to-date is a thing then.

## "Architecture decision log"
Don't generate AST, generate Python code. This is easier to write, easier to write, less verbose, and a lot easier to debug because error messages have had some attention. Other than "that's how you're supposed to do it according to theory", I can see no compelling reason to switch to ASTs other than performance, for which generating the Python code is fast enough right now.
