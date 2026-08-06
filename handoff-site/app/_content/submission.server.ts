import "server-only";

export function configuredSubmissionFormUrl(): string | null {
  const configured = process.env.SUBMISSION_FORM_URL?.trim();
  if (!configured) {
    return null;
  }
  const url = new URL(configured);
  if (url.protocol !== "https:" || url.username || url.password) {
    throw new Error("SUBMISSION_FORM_URL must be an HTTPS URL without embedded credentials");
  }
  return url.toString();
}
