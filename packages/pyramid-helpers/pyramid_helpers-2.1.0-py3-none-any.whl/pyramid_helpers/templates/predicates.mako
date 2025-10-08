<%inherit file="/site.mako" />\
<h2>${translate('Predicates')}</h2>

<div class="card mt-3">
    <div class="card-header">
        <h3 class="card-title h5 pt-2">Enum</h3>
    </div><!-- /.card-header -->
    <div class="card-body">
        <ul class="list-unstyled">
            <li><a href="${request.route_path('predicates.enum', predicate='value1')}">predicate=value1</a></li>
            <li><a href="${request.route_path('predicates.enum', predicate='value2')}">predicate=value2</a></li>
            <li><a href="${request.route_path('predicates.enum', predicate='value3')}">predicate=value3</a> (invalid)</li>
        </ul>
    </div><!-- /.card-body -->
    <div class="card-footer">
        ${translate('Current:')} <code>predicate=${request.matchdict.get('predicate')}</code>
    </div><!-- /.card-footer -->
</div><!-- /.card -->

<div class="card mt-5">
    <div class="card-header">
        <h3 class="card-title h5 pt-2">Numeric</h3>
    </div><!-- /.card-header -->
    <div class="card-body">
        <ul class="list-unstyled">
            <li><a href="${request.route_path('predicates.numeric-1', predicate1='1')}">predicate1=1</a></li>
            <li><a href="${request.route_path('predicates.numeric-1', predicate1='2')}">predicate1=2</a></li>
            <li><a href="${request.route_path('predicates.numeric-1', predicate1='a')}">predicate1=a</a> (invalid)</li>
            <li><a href="${request.route_path('predicates.numeric-2', predicate1='1', predicate2='3')}">predicate1=1, predicate2=3</a></li>
            <li><a href="${request.route_path('predicates.numeric-2', predicate1='2', predicate2='4')}">predicate1=2, predicate2=4</a></li>
            <li><a href="${request.route_path('predicates.numeric-2', predicate1='a', predicate2='3')}">predicate1=a, predicate2=3</a> (invalid)</li>
            <li><a href="${request.route_path('predicates.numeric-2', predicate1='1', predicate2='b')}">predicate1=1, predicate2=b</a> (invalid)</li>
            <li><a href="${request.route_path('predicates.numeric-2', predicate1='a', predicate2='b')}">predicate1=a, predicate2=b</a> (invalid)</li>
        </ul>
    </div><!-- /.card-body -->
    <div class="card-footer">
        ${translate('Current:')} <code>predicate1=${request.matchdict.get('predicate1')}</code>, <code>predicate2=${request.matchdict.get('predicate2')}</code>
    </div><!-- /.card-footer -->
</div><!-- /.card -->
