# Where should we write the GIF?
Output query.gif

Set FontSize 20
Set Width 1600
Set Height 600

Type "# Generate data classes for a query defined in example1.gql"
Sleep 1s
Enter

Type "cat gql/queries/example1.gql"
Sleep 1s
Enter
Sleep 3s

Type "qenerate code -i gql/introspection.json gql/"
Sleep 1s
Enter
Sleep 1s

Type "less gql/queries/example1.py"
Sleep 1s
Enter
Sleep 1s
Down 15
Sleep 2
Down 15
Sleep 2
Down 15
Sleep 2
Down 15
Sleep 2
Down 15
Sleep 3
Type "q"
Enter
