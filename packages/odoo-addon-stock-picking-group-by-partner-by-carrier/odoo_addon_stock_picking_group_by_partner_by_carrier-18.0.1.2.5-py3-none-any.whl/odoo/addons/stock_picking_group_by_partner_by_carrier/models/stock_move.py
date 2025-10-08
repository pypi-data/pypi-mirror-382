# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# Copyright 2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import namedtuple

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import groupby


class StockMove(models.Model):
    _inherit = "stock.move"

    # store the first group the move was in when created, used to keep track of
    # original group's name when creating a joint group for merged transfers,
    # and for cancellation of a sales order (to cancel only the moves related
    # to it)
    original_group_id = fields.Many2one(
        comodel_name="procurement.group",
        string="Original Procurement Group",
    )

    def write(self, vals):
        """
        During picking assignation, Odoo is overwriting the group on stock
        moves from found picking. Here, get the original group on stock moves.
        """
        if (
            self.env.context.get("picking_no_overwrite_partner_origin")
            and "picking_id" in vals
            and "group_id" not in vals
            and len(self.group_id) == 1
        ):
            vals["group_id"] = self.group_id.id
        res = super().write(vals)
        return res

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        # Prevent merging pulled moves. This allows to cancel a SO without
        # canceling pulled moves from other SO as we ensure they are not
        # merged.
        return super()._prepare_merge_moves_distinct_fields() + ["original_group_id"]

    def _assign_picking(self):
        result = super(
            StockMove, self.with_context(picking_no_overwrite_partner_origin=1)
        )._assign_picking()
        return result

    def _assign_picking_post_process(self, new=False):
        moves_by_picking = groupby(self, key=lambda m: m.picking_id)
        for picking, imoves in moves_by_picking:
            merged = picking._merge_procurement_groups()
            if merged:
                moves = self.browse(m.id for m in imoves)
                moves.picking_id._update_merged_origin()
                moves._on_assign_picking_message_link()
        # Ensure sale.order.picking_ids is properly read to ensure
        # action_confirm is called.
        # The m2m relation from stock.picking to sale.order is changed to a
        # stored computed field with depends but the reverse relation is not
        # defined as computed, so we need to flush the stored computed field so
        # that any read from sale.order will fetch the right value.
        self.picking_id.flush_recordset(["sale_ids"])
        res = super()._assign_picking_post_process(new=new)
        return res

    def _on_assign_picking_message_link(self):
        sales = self.sale_line_id.order_id
        if sales:
            self.picking_id.message_post_with_source(
                "mail.message_origin_link",
                render_values={"self": self.picking_id, "origin": sales, "edit": True},
                subtype_xmlid="mail.mt_note",
            )

    def _search_picking_for_assignation_domain(self):
        domain = super()._search_picking_for_assignation_domain()
        if (
            not self.picking_type_id.group_pickings
            or self.partner_id.disable_picking_grouping
            or (
                not self.picking_type_id.group_pickings_one
                and self.group_id.move_type == "one"
            )
        ):
            return domain

        # remove group
        tree_domain = expression._tree_from_domain(domain)
        tree_domain = [
            x for x in tree_domain if expression.is_operator(x) or x[1] != "group_id"
        ]
        domain = expression._tree_as_domain(tree_domain)

        grouping_domain = self._assign_picking_group_domain()

        res = domain + grouping_domain
        return res

    # TODO: this part and everything related to generic grouping
    # should be split into `stock_picking_group_by` module.
    def _assign_picking_group_domain(self):
        domain = [
            # same partner
            ("partner_id", "=", self.group_id.partner_id.id),
            # don't search on the procurement.group
        ]
        domain += self._domain_search_picking_handle_move_type()
        # same carrier only for outgoing transfers
        if self.picking_type_id.code == "outgoing":
            domain += [
                ("carrier_id", "=", self.group_id.carrier_id.id),
            ]
        if self.env.context.get("picking_no_copy_if_can_group"):
            # we are in the context of the creation of a backorder:
            # don't consider the current move's picking
            domain.append(("id", "!=", self.picking_id.id))
        return domain

    def _domain_search_picking_handle_move_type(self):
        """Hook to handle the move type.

        By default the move type is taken from the procurement group.
        Override to customize this behavior.
        """
        move_type = (
            self.group_id.move_type or self.picking_type_id.move_type or "direct"
        )
        return [("move_type", "=", move_type)]

    def _key_assign_picking(self):
        return (
            self.group_id.partner_id,
            PickingPolicy(id=self.group_id.move_type),
        ) + super()._key_assign_picking()


# we define a named tuple because the code in module stock expects the values in
# the tuple returned by _key_assign_picking to be records with an id attribute
PickingPolicy = namedtuple("PickingPolicy", ["id"])
