from __future__ import annotations

from mixam_sdk.item_specification.models.end_papers_component import EndPapersComponent
from mixam_sdk.item_specification.models.item_specification import ItemSpecification
from mixam_sdk.metadata.product.models.product_metadata import ProductMetadata
from mixam_sdk.metadata.product.models.validators.utils import select_binding_type_option_for_item_specification
from mixam_sdk.metadata.product.services.validation_result import ValidationResult
from .base import DefaultComponentValidator


class EndPapersComponentValidator(DefaultComponentValidator):
    def validate(self, product_metadata: ProductMetadata, item_specification: ItemSpecification, end_papers_component: EndPapersComponent, result: ValidationResult, base_path: str) -> None:
        # Ensure correct component type
        if not isinstance(end_papers_component, EndPapersComponent):
            result.add_error(
                path=base_path,
                message="Invalid component type for EndPapersComponentValidator: expected EndPapersComponent",
                code="validator.component.type_mismatch",
                expected="EndPapersComponent",
            )
            return
        # Primary-component substrate/lamination checks are handled by PrimaryComponentValidator.
        # Apply generic rules first.
        super().validate(product_metadata, item_specification, end_papers_component, result, base_path)

        # End Papers: colour id must be allowed; type/weight should be zero
        try:
            # Ensure binding type supports end papers (if a binding type option is selected)
            try:
                match = select_binding_type_option_for_item_specification(item_specification, product_metadata.cover_substrate_types, product_metadata.bound_metadata)
                bto = match.binding_type_option
                if bto is not None and not bto.supports_end_papers:
                    result.add_error(
                        path=f"{base_path}",
                        message="End papers are not supported by this binding type",
                        code="bound.end_papers.unsupported",
                    )
            except Exception:
                pass

            bm = product_metadata.bound_metadata
            if bm is not None:
                allowed_ep_colours = {m.end_paper_colour.value for m in bm.end_paper_metadata}
                if allowed_ep_colours and end_papers_component.substrate.colour_id not in allowed_ep_colours:
                    result.add_error(
                        path=f"{base_path}.substrate.colourId",
                        message="End paper colour not supported",
                        code="end_papers.colour.unavailable",
                        allowed=sorted(list(allowed_ep_colours)),
                    )
            # Per existing rule, end papers should not specify substrate type/weight ids
            if end_papers_component.substrate.type_id != 0 or end_papers_component.substrate.weight_id != 0:
                result.add_error(
                    path=f"{base_path}.substrate",
                    message="End papers should not have a substrate type id or weight id",
                    code="end_papers.substrate.ids_invalid",
                )
        except Exception:
            # Ignore metadata issues
            pass


__all__ = ["EndPapersComponentValidator"]
