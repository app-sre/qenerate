Output fragment.gif

Set FontSize 20
Set Width 1600
Set Height 600

Type "# Generate data classes for a query using a fragment"
Enter
Sleep 1
Type "# I.e., example2.gql uses the fragment defined in fragment1.gql"
Sleep 1
Enter

Sleep 1
Type "cat gql/fragments/fragment1.gql"
Sleep 1s
Enter
Sleep 3s

Type "cat gql/queries/example2.gql"
Sleep 1s
Enter
Sleep 3s

Type "qenerate code -i gql/introspection.json gql/"
Sleep 1s
Enter
Sleep 1s

Type "less gql/fragments/fragment1.py"
Sleep 1s
Enter
Sleep 1s
Down 15
Sleep 3
Type "q"
Enter

Type "less gql/queries/example2.py"
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
Sleep 3
Type "q"
Enter
