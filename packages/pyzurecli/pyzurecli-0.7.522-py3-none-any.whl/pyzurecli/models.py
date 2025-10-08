from dataclasses import dataclass
from pathlib import Path
from typing import Any

from annotated_dict import AnnotatedDict
from jinja2 import Environment, FileSystemLoader

CWD = Path(__file__).parent
TEMPLATES = CWD / "templates"
CWD_TEMPLATER = Environment(loader=FileSystemLoader(TEMPLATES))


class Email(AnnotatedDict):
    id: str
    subject: str
    body: dict
    sender: dict

    # Recipients
    toRecipients: list
    ccRecipients: list
    bccRecipients: list

    # Timestamps
    receivedDateTime: str
    sentDateTime: str

    # Metadata
    isRead: bool
    hasAttachments: bool
    importance: str
    isDraft: bool
    conversationId: str
    conversationIndex: str
    webLink: str
    internetMessageId: str

class Person(AnnotatedDict):
    id: str
    displayName: str
    givenName: str
    surname: str
    userPrincipalName: str

    # Contact information
    scoredEmailAddresses: list
    phones: list
    postalAddresses: list
    websites: list
    imAddress: str

    # Professional information
    jobTitle: str
    companyName: str
    yomiCompany: str
    department: str
    officeLocation: str
    profession: str

    # Personal information
    birthday: str
    personNotes: str
    isFavorite: bool

    # Classification
    personType: dict

    @property
    def primary_email(self):
        """Get the primary email address with highest relevance score"""
        if not self.scoredEmailAddresses:
            return None

        # Sort by relevance score and return the highest
        sorted_emails = sorted(
            self.scoredEmailAddresses,
            key=lambda x: x.get('relevanceScore', 0),
            reverse=True
        )
        return sorted_emails[0]['address']

    @property
    def relevance_score(self):
        """Get the highest relevance score for this person"""
        if not self.scoredEmailAddresses:
            return 0

        return max(email.get('relevanceScore', 0) for email in self.scoredEmailAddresses)

    @property
    def person_class(self):
        """Get the person class (Person, Group, etc.)"""
        return self.personType.get('class', 'Unknown') if self.personType else 'Unknown'

    @property
    def person_subclass(self):
        """Get the person subclass (OrganizationUser, UnifiedGroup, etc.)"""
        return self.personType.get('subclass', 'Unknown') if self.personType else 'Unknown'

    @property
    def is_group(self):
        """Check if this is a group rather than an individual person"""
        return self.person_class == 'Group'

    @property
    def is_organization_user(self):
        """Check if this is an organization user"""
        return self.person_subclass == 'OrganizationUser'

    @property
    def full_name(self):
        """Get the full name, falling back to displayName if givenName/surname not available"""
        if self.givenName and self.surname:
            return f"{self.givenName} {self.surname}"
        return self.displayName or "Unknown"

    @property
    def business_phone(self):
        """Get the primary business phone number"""
        if not self.phones:
            return None

        # Look for business phone first
        for phone in self.phones:
            if phone.get('type') == 'business':
                return phone.get('number')

        # Fall back to first available phone
        return self.phones[0].get('number') if self.phones else None

    @property
    def contact_summary(self):
        """Get a summary of contact information"""
        summary = {
            'name': self.full_name,
            'email': self.primary_email,
            'phone': self.business_phone,
            'title': self.jobTitle,
            'department': self.department,
            'company': self.companyName,
            'office': self.officeLocation,
            'type': self.person_class,
            'relevance': self.relevance_score
        }
        return {k: v for k, v in summary.items() if v}  # Remove None/empty values

    @property
    def view(self):
        """Render the person as HTML"""
        template = CWD_TEMPLATER.get_template("person.html")
        return template.render(contact_summary=self.contact_summary)

    def __str__(self):
        return f"{self.full_name} ({self.primary_email})"

    def __repr__(self):
        return f"Person(name='{self.full_name}', email='{self.primary_email}', type='{self.person_class}')"


class Me(AnnotatedDict):
    businessPhones: Any
    displayName: str
    givenName: str
    jobTitle: str
    mail: str
    mobilePhone: Any
    officeLocation: Any
    preferredLanguage: Any
    surname: str
    userPrincipalName: Any
    id: str

class Organization(AnnotatedDict):
    id: str
    deletedDateTime: Any
    businessPhones: Any
    city: Any
    country: Any
    countryLetterCode: Any
    createdDateTime: Any
    defaultUsageLocation: Any
    displayName: str
    isMultipleDataLocationsForServicesEnabled: Any
    marketingNotificationEmails: Any
    onPremisesLastSyncDateTime: Any
    onPremisesSyncEnabled: Any
    partnerTenantType: Any
    postalCode: Any
    preferredLanguage: Any
    securityComplianceNotificationMails: Any
    securityComplianceNotificationPhones: Any
    state: Any
    street: Any
    technicalNotificationMails: Any
    tenantType: str
    directorySizeQuota: Any
    privacyProfile: Any
    assignedPlans: Any
    onPremisesSyncStatus: Any
    provisionedPlans: Any
    verifiedDomains: Any
