# Queries

+ Quantas classes estão definidas na Ontologia?
```
select (count(*) as ?s)
where {
    ?s a owl:Class .
}
```

+ Quantas Object Properties estão definidas na Ontologia?
```
select (distinct count(*) as ?p)
where {
    ?s ?p ?o .
}
```

+ Quantos indivíduos existem na tua ontologia?
```
select (count(*) as ?s)
where {
    ?s a owl:NamedIndividual .
}
```

+ Quem planta tomates?
```
select ?s
where {
    ?s :cultiva :tomate.
}
```

+ Quem contrata trabalhadores temporários?
```
select distinct ?s
where {
    ?s :contrata ?o .
    ?o a :TrabalhadorTemp .
}
```