Given a boolean formula in propositional logic using the following symbols:  
  * ~ for 'negation'  
  * & for 'and'  
  * v for 'or'  
  * -> for 'implies'  
  * ( ) to control order of operations
  * A[1-9][0-9]* for variables  

returns a formula in connjunctive normal form using DIMACS format to be used as input compatible with MiniSAT.
MiniSAT will return whether or not this formula is satisfiable.

To run this program:
1. Run 'python ConvertToDimacs.py'
2. When prompted, type in the boolean formula
