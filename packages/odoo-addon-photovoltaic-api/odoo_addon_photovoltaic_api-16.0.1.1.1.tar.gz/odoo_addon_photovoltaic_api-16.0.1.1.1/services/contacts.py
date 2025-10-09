import logging
from odoo.addons.base_rest import restapi
from odoo.addons.component.core import Component
from ..pydantic_models.contact import Contact

_logger = logging.getLogger(__name__)

EXCLUDED_CONTACT_FIELDS = {'representative', 'interests', 'message_notes', 'tags', 'state', 'country'}
RETURN_CONTACT_FIELDS = ['id', 'firstname', 'lastname', 'vat', 'email', 'mobile', 'phone', 'alias']


class ContactService(Component):
    _inherit = 'base.rest.service'
    _name = 'contacts.service'
    _usage = 'contacts'
    _collection = 'photovoltaic_api.services'

    @restapi.method(
        [(['/'], 'POST')],
        input_param=restapi.PydanticModel(Contact),
        auth='api_key'
    )
    # Will upsert contact based on vat or email
    def create(self, contact_data):
        contact_dict = self.build_contact_dict(contact_data)
        existing_contacts = self.find_existing_contacts(contact_dict)
        if (len(existing_contacts) == 0):
            contact = self.env['res.partner'].create(contact_dict)
        else:
            contact = self.update_existing_contact(contact_dict, existing_contacts)
        if contact_data.message_notes:
            self.create_message_notes_on_contact(contact, contact_data.message_notes)
        return contact.read(RETURN_CONTACT_FIELDS)[0]

    def build_contact_dict(self, contact: Contact):
        contact_dict = contact.model_dump(exclude_unset=True, exclude=EXCLUDED_CONTACT_FIELDS)

        if contact.country:
            contact_dict = self.include_country_id_in_contact(contact_dict, contact.country)
        if 'country_id' in contact_dict and contact.state:
            contact_dict = self.include_state_id_in_contact(contact_dict, contact.state)
        if contact.tags:
            contact_dict = self.include_tags_in_contact(contact_dict, contact.tags)
        return contact_dict

    def include_country_id_in_contact(self, contact: dict, country: str):
        country_id = self._search_country(country)
        if country_id:
            contact['country_id'] = country_id
        return contact

    def include_state_id_in_contact(self, contact: dict, state: str):
        if state:
            state_id = self._search_state(state, contact['country_id'])
            if state_id:
                contact['state_id'] = state_id
        return contact

    def include_tags_in_contact(self, contact: dict, tags):
        found_tags = self.env['res.partner.category'].search([('name', 'in', tags)])
        if len(found_tags) != len(tags):
            found_tags_names = [tag.name for tag in found_tags]
            for tag in tags:
                if tag not in found_tags_names:
                    _logger.warn(f'Cannot assign tag {tag}, since it doesn\'t exist in Odoo')
        _logger.debug(f"Adding tags {[tag.name for tag in found_tags]} to contact {contact['firstname']}")
        contact['category_id'] = [(4, tag.id, 0) for tag in found_tags]
        return contact

    def find_existing_contacts(self, contact: dict):
        if 'vat' in contact:
            contact['vat'] = contact['vat'].upper()
            existing_contacts = self.env['res.partner'].search([('vat', '=ilike', contact['vat'])])
            if len(existing_contacts) == 0:
                if 'email' not in contact:
                    return []
                existing_contacts = self.env['res.partner'].search([('email', '=', contact['email']), ('vat', '=', False)])
            else:
                del contact['vat']
        elif 'email' in contact:
            existing_contacts = self.env['res.partner'].search([('email', '=', contact['email'])])
        return existing_contacts

    def update_existing_contact(self, contact: dict, existing_contacts):
        contact_to_update = existing_contacts[0]
        # More than one entry -> Add warning note
        if len(existing_contacts) > 1:
            self.add_duplication_message_to_contact(contact_to_update, existing_contacts)
        _logger.debug(f"[{contact_to_update.email}] : Updating existing entry [{contact_to_update.id}]")
        # Concatenate the provided comment with the existing ones
        if 'comment' in contact:
            contact['comment'] = f'{contact_to_update.comment}\n\n{contact["comment"]}'
        contact_to_update.write(contact)
        return contact_to_update

    def add_duplication_message_to_contact(self, contact, duplicated_contacts):
        warn_msg = f"[{contact.email}] : {len(duplicated_contacts)} entries : {duplicated_contacts}"
        _logger.warn(warn_msg)
        contact.message_post(body=warn_msg)  # TODO - Warning amarillo

    def create_message_notes_on_contact(self, contact, message_notes):
        contact.message_post(body=message_notes)

    def _search_zip_id(self, zip: str):
        zip_ids = self.env['res.city.zip'].search([('name', 'ilike', zip)])
        if len(zip_ids) > 0:
            return zip_ids[0].id
        return None

    def _search_country(self, country: str):
        country_ids = self.env['res.country'].search([('name', 'ilike', country)])
        if len(country_ids) > 0:
            return country_ids[0].id
        return None

    def _search_state(self, state: str, country_id: int):
        state_ids = self.env['res.country.state'].search([('name', 'ilike', state), ('country_id', '=', country_id)])
        if len(state_ids) > 0:
            return state_ids[0].id
        return None
