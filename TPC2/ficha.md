# Ficha

## Prefixos
```
PREFIX historia: <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix : <http://www.semanticweb.org/andre/ontologies/2015/6/historia#>
```

## Questões

### 1 - Quantos triplos existem na Ontologia?
6603
```
select (count(*) as ?c)
where {
    ?s ?p ?o .
}
```

### 2 - Que classes estão definidas?
(102)
```
select ?classe
where {
    ?classe rdf:type owl:Class .
}
```

### 3 - Que propriedades tem a classe "Rei"?
(14 + rdf:type + owl:topObjectProperty)
```
select distinct ?prop
where {
    ?s rdf:type :Rei .
    ?s ?prop ?o .
}
order by ?prop
```
 
### 4 - Quantos reis aparecem na ontologia?
32
```
select (count(?s) as ?c)
where {
    ?s rdf:type :Rei .
}
```

### 5 - Calcula uma tabela com o seu nome, data de nascimento e cognome.
```
select ?n ?dn ?c
where {
    ?s rdf:type :Rei .
    ?s :nome ?n .
    ?s :nascimento ?dn .
    ?s :cognomes ?c .
}



select ?n ?dn ?c
where {
    ?s rdf:type :Rei ;
        :nome ?n ;
        :nascimento ?dn ;
        :cognomes ?c .
}
```

### 6 - Acrescenta à tabela anterior a dinastia em que cada rei reinou.
```
select ?n ?dn ?c ?d ?dnome
where {
    ?s rdf:type :Rei .
    ?s :nome ?n .
    ?s :nascimento ?dn .
    ?s :cognomes ?c .
    ?r :dinastia ?d .
    ?r :temMonarca ?s.
    ?d :nome ?dnome
}
order by ?d
```

### 7 - Qual a distribuição de reis pelas 4 dinastias?
1 - 9
2 - 10 / 8
3 - 3
4 - 12
```
select ?d (count(?s) as ?c)
where {
    ?s rdf:type :Rei .
    ?r :temMonarca ?s .
    ?r :dinastia ?d .
}
group by ?d
order by ?d



select ?d (count(?s) as ?c)
where {
    ?s rdf:type :Rei .
    ?s :temReinado/:dinastia/:nome ?d .
}
group by ?d
```

### 8 - Lista os descobrimentos (sua descrição) por ordem cronológica.
```
select ?s ?n
where {
    ?s rdf:type :Descobrimento .
    ?s :notas ?n .
    ?s :data ?d .
}
order by ?d
```

### 9 - Lista as várias conquistas, nome e data, com o nome do rei que reinava no momento.
```
select ?n ?d ?nr
where {
    ?s rdf:type :Conquista .
    ?s :nome ?n .
    ?s :data ?d .
    ?s :temReinado ?r .
    ?r :temMonarca ?m .
    ?m :nome ?nr .
}
order by ?d
```

### 10 - Calcula uma tabela com o nome, data de nascimento e número de mandatos de todos os presidentes portugueses.
```
select ?n ?d (count(?m) as ?c)
where {
    ?s rdf:type :Presidente .
    ?s :nome ?n .
    ?s :nascimento ?d .
    ?s :mandato ?m
}
group by ?s ?n ?d
order by ?n
```

### 11 - Quantos mandatos teve o presidente Sidónio Pais? Em que datas iniciaram e terminaram esses mandatos?
```
select (count(?m) as ?c)
where {
    ?s rdf:type :Presidente .
    ?s :nome ?n .
    FILTER regex(?n, ".*Sidónio.*Pais.*", "i") .
    ?s :mandato ?m
}
group by ?s



select ?m ?c ?f
where {
    ?s rdf:type :Presidente .
    ?s :nome ?n .
    FILTER regex(?n, ".*Sidónio.*Pais.*", "i") .
    ?s :mandato ?m .
    ?m :comeco ?c .
    ?m :fim ?f .
}
```

### 12 - Quais os nomes dos partidos politicos presentes na ontologia?
```
select distinct ?n
where {
    ?s rdf:type :Partido .
    ?s :nome ?n
}
order by ?n
```

### 13 - Qual a distribuição dos militantes por cada partido politico?
```
select ?n (count(?m) as ?c)
where {
    ?s rdf:type :Partido .
    ?s :nome ?n .
    ?s :temMilitante ?m .
}
group by ?s ?n
order by ?n
```

### 14 - Qual o partido com maior número de presidentes militantes?
```
select ?n (count(?m) as ?c)
where {
    ?s rdf:type :Partido .
    ?s :nome ?n .
    ?s :temMilitante ?m .
}
group by ?s ?n
order by desc(?c)
limit 1
```