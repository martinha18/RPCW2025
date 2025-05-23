# Ex 11

+ Quantas doenças estão presentes na ontologia? 42

```
PREFIX : <http://www.example.org/disease-ontology#>

select (count(?d) as ?c)
where{
    ?d a :Disease .
}
```


+ Que doenças estão associadas ao sintoma "yellowish_skin"?

```
PREFIX : <http://www.example.org/disease-ontology#>

select ?d
where{
    ?d a :Disease ;
       :hasSymptom :yellowish_skin
}
```


+ Que doenças estão associadas ao tratamento "exercise"?

```
PREFIX : <http://www.example.org/disease-ontology#>

select ?d
where{
    ?d a :Disease ;
       :hasTreatment :exercise
}
```


+ Produz uma lista ordenada alfabeticamente com o nome dos doentes.

```
PREFIX : <http://www.example.org/disease-ontology#>

select ?n
where{
    ?d a :Patient ;
    	:name ?n .
}
order by ?n
```


# Ex 12

```
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://www.example.org/disease-ontology#>

construct {
    ?patient :hasDisease ?d
}
where {
  ?patient a :Patient .
  ?d a :Disease .   
  {
    SELECT ?patient ?d (COUNT(?symptomD) AS ?matchingSymptomCount)
    WHERE {
      ?patient :exhibitsSymptom ?symptomP .
      ?d a :Disease .
      ?d :hasSymptom ?symptomD .
      FILTER(?symptomD = ?symptomP)
    }
    GROUP BY ?patient ?d
  }
  FILTER (?matchingSymptomCount > 3)
}

PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://www.example.org/disease-ontology#>

insert {
    ?patient :hasDisease ?d
}
where {
  ?patient a :Patient .
  ?d a :Disease .   
  {
    SELECT ?patient ?d (COUNT(?symptomD) AS ?matchingSymptomCount)
    WHERE {
      ?patient :exhibitsSymptom ?symptomP .
      ?d a :Disease .
      ?d :hasSymptom ?symptomD .
      FILTER(?symptomD = ?symptomP)
    }
    GROUP BY ?patient ?d
  }
  FILTER (?matchingSymptomCount > 3)
}
```


# Ex 13

```
select ?d (count(?p) as ?c)
where {
	?p :hasDisease ?d .
}
groupby(?d)
order by desc(?c)
```


# Ex 14

```
PREFIX : <http://www.example.org/disease-ontology#>

select ?s (count(?d) as ?c)
where {
	?d :hasSymptom ?s .
}
groupby(?s)
order by desc(?c)
```


# Ex 15

```
select ?t (count(?d) as ?c)
where {
	?d :hasTreatment ?t .
}
groupby(?t)
order by desc(?c)
```