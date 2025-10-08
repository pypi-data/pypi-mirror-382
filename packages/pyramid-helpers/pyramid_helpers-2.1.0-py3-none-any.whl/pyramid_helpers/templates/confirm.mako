<%inherit file="/site.mako"/>\
<%def name="foot()">
${parent.foot()}\
<script type="text/javascript">
const modalDiv = document.getElementById('confirm-dialog');

modalDiv.addEventListener('hidden.bs.modal', e => {
    let self = e.target;

    // Perform cancel action when the dialog is closed by user
    self.querySelector('button[name="cancel"]').click();
});

const modal = new bootstrap.Modal(modalDiv);
modal.show();
</script>
</%def>\
<div id="confirm-dialog" class="modal modal-lg" role="dialog">
    <div class="modal-dialog">
        <div class="modal-content">
            <form method="post" role="form">
                <div class="modal-header border-0">
                    <h4 class="modal-title h5">${translate('Confirmation')}</h4>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-hidden="true"></button>
                </div>
                <div class="modal-body">
                    ${question}
% if note:
                    <br><br>
                    <em>${note | n}</em>
% endif
                </div>
                <div class="modal-footer border-0 text-end">
                    <button type="submit" class="btn btn-secondary me-2" name="cancel">${translate('Cancel')}</button>
                    <button type="submit" class="btn btn-primary" name="confirm">${translate('Ok')}</button>
                </div>
            </form>
        </div><!-- /.modal-content -->
    </div><!-- /.modal-dialog -->
</div><!-- /.modal -->
