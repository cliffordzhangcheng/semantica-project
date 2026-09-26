"""Project reviewed, redacted source assertions without inventing settlement.

Raw-source hash/locator verification is performed privately at admission. Public
validation checks scope, types and projection integrity; it cannot authenticate
unavailable confidential originals and must not claim to do so.
"""
from datetime import date
from decimal import Decimal, InvalidOperation
import re

TRUTH_STATES = frozenset({
    'UNKNOWN', 'REQUIRED', 'VERIFIED', 'USER_ENTERED',
    'CANDIDATE', 'CONFLICTED', 'UNALLOCATED',
})


def require(value, message):
    if not value:
        raise ValueError(message)


def day(value):
    require(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), 'Invalid source date')
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError('Invalid calendar date') from exc


def money(value):
    require(isinstance(value, str) and re.fullmatch(r'\d+\.\d{2}', value), 'Invalid monetary amount')
    try:
        require(Decimal(value).is_finite() and Decimal(value) >= 0, 'Invalid monetary amount')
    except InvalidOperation as exc:
        raise ValueError('Invalid monetary amount') from exc


def project(sources, job_id, containers):
    """Recovered facts remain assertions with explicit support and date basis."""
    fields = {'evidence_id', 'kind', 'source_date', 'support_strength', 'case_refs',
              'bindings', 'private_ledger_ref', 'sensitivity', 'redaction_status',
              'truth_status', 'facts'}
    allowed = {
        'RECEIPT_REPORT': ('QUOTED_CREDITOR_RECEIPT_ATTESTATION',
                           {'reported_on', 'amount', 'currency', 'bank_value_date', 'allocations', 'balance_claim'}),
        'BILLING_DOCUMENT': ('DIRECT_BILLING_DOCUMENT',
                            {'job_id', 'charge_type', 'document_type', 'amount', 'currency', 'offhire_dates', 'conflicts'}),
        'DOCUMENT_VERSION_CONFLICT': ('DIRECT_DOCUMENT_VERSION_CONFLICT',
                                      {'job_id', 'document_ref', 'amounts', 'currency'}),
        'PAYABLE_BOOKING': ('CARRIER_BOOKING_EMAIL_AND_VISUALLY_READ_SCREENSHOT',
                           {'job_id', 'amount', 'currency', 'document_date', 'posted_on', 'due_on', 'paid', 'invoice_ref', 'conflicts'}),
    }
    result = {'receipts': [], 'payments': [], 'billing_documents': [],
              'observations': [], 'operational_assertions': [],
              'financial_assertions': [], 'reconciliation_issues': []}
    seen = set()
    for source in sorted(sources, key=lambda s: s['evidence_id']):
        require(set(source) == fields, 'Unexpected recovered source shape')
        sid, kind, facts = source['evidence_id'], source['kind'], source['facts']
        require(isinstance(sid, str) and sid not in seen, 'Duplicate recovered evidence')
        seen.add(sid)
        require(kind in allowed, 'Unknown recovered source kind')
        strength, fact_fields = allowed[kind]
        require(source['support_strength'] == strength and set(facts) == fact_fields, 'Unsupported source semantics')
        require(source['redaction_status'] == 'REDACTED' and source['sensitivity'] == 'CONFIDENTIAL', 'Unsafe recovered source')
        truth = source['truth_status']
        require(isinstance(truth, dict) and truth and set(truth.values()) <= TRUTH_STATES,
                'Invalid shared truth status')
        require(source['private_ledger_ref'].startswith('N524-'), 'Missing private lineage')
        require(source['bindings'] and all(set(b) == {'sha256', 'locator'} and
                re.fullmatch(r'[0-9a-f]{64}', b['sha256']) and b['locator'].strip()
                for b in source['bindings']), 'Missing source hash or locator')
        refs = source['case_refs']
        require(isinstance(refs, list) and job_id in refs and len(refs) == len(set(refs)), 'Cross-case evidence leakage')
        require(all(isinstance(ref, str) and ref.startswith('JOB-') for ref in refs), 'Invalid case reference')
        if kind != 'RECEIPT_REPORT':
            require(refs == [job_id] and facts['job_id'] == job_id, 'Cross-case evidence leakage')
        if source['source_date'] is not None:
            day(source['source_date'])
        if kind != 'DOCUMENT_VERSION_CONFLICT':
            require(source['source_date'] is not None, 'Missing source report date')
            money(facts['amount'])
        require(facts['currency'] == 'USD', 'Unsupported source currency')
        common = {'evidence_ref': sid, 'support_strength': strength,
                  'source_truth_status': truth}
        if kind == 'RECEIPT_REPORT':
            require(truth == {'assertion': 'CANDIDATE', 'evidence': 'VERIFIED',
                    'entry': 'USER_ENTERED', 'allocation': 'UNALLOCATED',
                    'value_date': 'UNKNOWN'}, 'Receipt truth states changed')
            day(facts['reported_on'])
            require(facts['reported_on'] == source['source_date'], 'Receipt report date differs from source')
            require(facts['bank_value_date'] is None, 'Unsupported bank value date')
            require(facts['allocations'] == [], 'Unsupported payment allocation')
            balance = facts['balance_claim']
            require(set(balance) == {'job_id', 'as_of', 'amount', 'currency'} and
                    balance['job_id'] == job_id and balance['as_of'] == facts['reported_on'] and
                    balance['currency'] == facts['currency'], 'Unsupported balance claim')
            money(balance['amount'])
            receipt_id = 'RECEIPT-' + sid
            result['receipts'].append({'receipt_id': receipt_id, 'record_type': 'RECEIPT',
                'assertion_status': 'CANDIDATE', 'evidence_status': 'VERIFIED',
                'entry_mode': 'USER_ENTERED', 'allocation_status': 'UNALLOCATED',
                'value_date_status': 'UNKNOWN',
                'case_refs': refs, 'amount': facts['amount'], 'currency': facts['currency'],
                'reported_on': facts['reported_on'], 'bank_value_date': None, 'allocations': [], **common})
            result['financial_assertions'].append({'assertion_type': 'CREDITOR_BALANCE_CLAIM',
                **balance, 'assertion_status': 'CANDIDATE',
                'current_balance_status': 'UNKNOWN', **common})
            result['reconciliation_issues'].append({'code': 'RECEIPT_ALLOCATION_UNRESOLVED',
                'status': 'REQUIRED', 'allocation_status': 'UNALLOCATED', **common})
            result['observations'].append({'observation_id': 'OBS-REPORTED-' + sid,
                'record_type': 'OBSERVATION', 'observation_type': 'RECEIPT_REPORTED',
                'scope': 'receipt:' + receipt_id, 'observed_on': facts['reported_on'],
                'date_precision': 'day', 'assertion_status': 'CANDIDATE',
                'evidence_status': 'VERIFIED', **common})
        elif kind == 'BILLING_DOCUMENT':
            require(facts['document_type'] == 'PROFORMA_INVOICE' and facts['charge_type'] in {'REPAIR', 'PER_DIEM'}, 'Invalid billing document')
            require(set(facts['conflicts']) <= {'NUMERIC_AND_WRITTEN_TOTAL_DIFFER', 'CHARGING_PERIOD_REQUIRES_RECONCILIATION'}, 'Unknown billing conflict')
            expected_assertion = 'CONFLICTED' if facts['conflicts'] else 'CANDIDATE'
            require(truth == {'assertion': expected_assertion, 'evidence': 'VERIFIED',
                    'reconciliation': 'REQUIRED'}, 'Billing truth states changed')
            result['billing_documents'].append({'document_id': 'DOC-' + sid,
                'issued_on': source['source_date'], 'job_id': job_id, 'charge_type': facts['charge_type'],
                'document_type': facts['document_type'], 'numeric_total': facts['amount'],
                'currency': facts['currency'], 'assertion_status': expected_assertion,
                'evidence_status': 'VERIFIED', 'reconciliation_status': 'REQUIRED', **common})
            for item in facts['offhire_dates']:
                require(set(item) == {'container', 'occurred_on', 'locator'} and
                        item['container'] in containers and item['locator'].strip(), 'Invalid off-hire scope or locator')
                day(item['occurred_on'])
                require(item['occurred_on'] <= source['source_date'], 'Off-hire assertion after source date')
                require(facts['charge_type'] == 'PER_DIEM', 'Off-hire assertion not supported by this billing type')
                assertion = {'assertion_type': 'BILLING_REPORTED_OFF_HIRE',
                    'record_type': 'OBSERVATION', **item, 'reported_on': source['source_date'],
                    'assertion_status': 'CANDIDATE', 'evidence_status': 'VERIFIED', **common}
                result['operational_assertions'].append(assertion)
                result['observations'].append({'observation_id': 'OBS-OFFHIRE-' + item['container'],
                    'record_type': 'OBSERVATION', 'observation_type': 'BILLING_REPORTED_OFF_HIRE',
                    'scope': 'container:' + item['container'], 'observed_on': item['occurred_on'],
                    'reported_on': source['source_date'], 'date_precision': 'day',
                    'assertion_status': 'CANDIDATE', 'evidence_status': 'VERIFIED', **common})
            result['reconciliation_issues'].extend(
                {'code': code, 'status': 'CONFLICTED', **common} for code in facts['conflicts'])
        elif kind == 'DOCUMENT_VERSION_CONFLICT':
            require(truth == {'assertion': 'CONFLICTED', 'evidence': 'VERIFIED',
                    'reconciliation': 'REQUIRED'}, 'Document conflict truth states changed')
            require(len(facts['amounts']) >= 2 and len(set(facts['amounts'])) >= 2 and facts['document_ref'], 'Invalid version conflict')
            for amount in facts['amounts']:
                money(amount)
            # Alternative versions are not additional financial obligations.
            result['reconciliation_issues'].append({'code': 'DOCUMENT_VERSION_CONFLICT',
                'status': 'CONFLICTED', 'document_ref': facts['document_ref'],
                'alternative_amounts': facts['amounts'], **common})
        elif kind == 'PAYABLE_BOOKING':
            require(truth == {'assertion': 'CONFLICTED', 'evidence': 'VERIFIED',
                    'payment': 'UNKNOWN', 'reconciliation': 'REQUIRED'},
                    'Payable booking truth states changed')
            for key in ('document_date', 'posted_on', 'due_on'):
                day(facts[key])
            require(facts['document_date'] <= facts['posted_on'] <= source['source_date'], 'Out-of-order booking dates')
            require(facts['due_on'] >= facts['document_date'], 'Out-of-order due date')
            require(facts['paid'] is None and facts['invoice_ref'] is None, 'Booking cannot establish payment or exact invoice allocation')
            require(facts['conflicts'] == ['PROSE_AND_SCREENSHOT_YEAR_DIFFER'], 'Booking date conflict hidden')
            result['financial_assertions'].append({'assertion_type': 'CARRIER_PAYABLE_BOOKING',
                'record_type': 'OBSERVATION', **facts, 'reported_on': source['source_date'],
                'assertion_status': 'CONFLICTED', 'evidence_status': 'VERIFIED',
                'payment_status': 'UNKNOWN', **common})
            result['observations'].append({'observation_id': 'OBS-BOOKED-' + sid,
                'record_type': 'OBSERVATION', 'observation_type': 'PAYABLE_BOOKED',
                'scope': 'job:' + job_id, 'observed_on': source['source_date'],
                'date_precision': 'day', 'assertion_status': 'CONFLICTED',
                'evidence_status': 'VERIFIED', 'payment_status': 'UNKNOWN', **common})
            result['reconciliation_issues'].extend(
                {'code': code, 'status': 'CONFLICTED', **common} for code in facts['conflicts'])
    units = [item['container'] for item in result['operational_assertions']]
    require(len(units) == len(set(units)), 'Duplicate or conflicting per-container assertions require reconciliation')
    claims = [item for item in result['financial_assertions'] if item['assertion_type'] == 'CREDITOR_BALANCE_CLAIM']
    for claim in claims:
        documents = [item for item in result['billing_documents']
                     if item['issued_on'] == claim['as_of'] and item['currency'] == claim['currency']]
        if documents:
            total = sum((Decimal(item['numeric_total']) for item in documents), Decimal('0'))
            result['financial_assertions'].append({
                'assertion_type': 'BILLING_TOTAL_COMPARISON', 'as_of': claim['as_of'],
                'job_id': job_id, 'currency': claim['currency'], 'billing_total': f'{total:.2f}',
                'claimed_balance': claim['amount'], 'numeric_totals_match': total == Decimal(claim['amount']),
                'assertion_status': 'VERIFIED' if total == Decimal(claim['amount']) else 'CONFLICTED',
                'settlement_status': 'UNKNOWN',
                'evidence_refs': [claim['evidence_ref']] + [item['evidence_ref'] for item in documents],
            })
            if total != Decimal(claim['amount']):
                result['reconciliation_issues'].append({'code': 'BILLING_BALANCE_MISMATCH',
                    'status': 'CONFLICTED', 'evidence_ref': claim['evidence_ref'],
                    'support_strength': 'DERIVED_NUMERIC_COMPARISON'})
    return result
