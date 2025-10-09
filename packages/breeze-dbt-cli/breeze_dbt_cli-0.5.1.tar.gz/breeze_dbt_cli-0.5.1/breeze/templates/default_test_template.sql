{% test test_name(model, column_name) %} 

    select *
    from {{ model }}
    where {{ column_name }} is something

{% endtest %}