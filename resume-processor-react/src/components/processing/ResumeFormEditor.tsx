import React, { useState, useEffect, ChangeEvent } from 'react'
import { Button } from '../ui/button'
import { Input } from '../ui/input'
import { Textarea } from '../ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Plus, Trash2, Save, Download } from 'lucide-react'
import { toast } from 'sonner'

interface ResumeFormEditorProps {
  data: any
  onSave: () => void
  onExport: () => void
}

interface Experience {
  company: string
  title: string
  start_date?: string
  end_date?: string
  description?: string
  achievements?: string[]
}

interface Education {
  degree: string
  institution: string
  start_date?: string
  end_date?: string
  gpa?: string
  relevant_coursework?: string[]
}

const ResumeFormEditor: React.FC<ResumeFormEditorProps> = ({ data, onSave, onExport }) => {
  const [formData, setFormData] = useState<any>(data || {})
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    setFormData(data || {})
    setHasChanges(false)
  }, [data])

  const updateField = (field: string, value: any) => {
    setFormData((prev: any) => ({ ...prev, [field]: value }))
    setHasChanges(true)
  }

  const updateArrayField = (field: string, index: number, value: any) => {
    setFormData((prev: any) => {
      const newArray = [...(prev[field] || [])]
      newArray[index] = value
      return { ...prev, [field]: newArray }
    })
    setHasChanges(true)
  }

  const addArrayItem = (field: string, defaultItem: any) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: [...(prev[field] || []), defaultItem]
    }))
    setHasChanges(true)
  }

  const removeArrayItem = (field: string, index: number) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: prev[field]?.filter((_: any, i: number) => i !== index) || []
    }))
    setHasChanges(true)
  }

  const handleSave = () => {
    // Update the global state
    Object.assign(data, formData)
    setHasChanges(false)
    onSave()
    toast.success('Changes saved successfully!')
  }

  return (
    <div className="space-y-6">
      {/* Basic Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">👤 Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
              <Input
                id="name"
                value={formData.name || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('name', e.target.value)}
                placeholder="Enter your full name"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <Input
                id="email"
                type="email"
                value={formData.email || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('email', e.target.value)}
                placeholder="your.email@example.com"
              />
            </div>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
              <Input
                id="phone"
                value={formData.phone || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('phone', e.target.value)}
                placeholder="+1 (555) 123-4567"
              />
            </div>
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">Location</label>
              <Input
                id="location"
                value={formData.location || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('location', e.target.value)}
                placeholder="City, State/Country"
              />
            </div>
            <div>
              <label htmlFor="linkedin" className="block text-sm font-medium text-gray-700 mb-1">LinkedIn</label>
              <Input
                id="linkedin"
                value={formData.linkedin || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('linkedin', e.target.value)}
                placeholder="linkedin.com/in/yourprofile"
              />
            </div>
            <div>
              <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-1">Website</label>
              <Input
                id="website"
                value={formData.website || ''}
                onChange={(e: ChangeEvent<HTMLInputElement>) => updateField('website', e.target.value)}
                placeholder="yourwebsite.com"
              />
            </div>
          </div>
          <div>
            <label htmlFor="summary" className="block text-sm font-medium text-gray-700 mb-1">Professional Summary</label>
            <Textarea
              id="summary"
              value={formData.summary || ''}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateField('summary', e.target.value)}
              placeholder="Write a compelling professional summary..."
              rows={4}
            />
          </div>
        </CardContent>
      </Card>

      {/* Experience */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">💼 Work Experience</CardTitle>
          <Button
            onClick={() => addArrayItem('experience', {
              company: '',
              title: '',
              start_date: '',
              end_date: '',
              description: '',
              achievements: []
            })}
            size="sm"
            variant="outline"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Experience
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {(formData.experience || []).map((exp: Experience, index: number) => (
            <div key={index} className="border rounded-lg p-4 space-y-4">
              <div className="flex justify-between items-start">
                <h4 className="font-medium">Experience #{index + 1}</h4>
                <Button
                  onClick={() => removeArrayItem('experience', index)}
                  size="sm"
                  variant="destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Company *</label>
                  <Input
                    value={exp.company || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('experience', index, { ...exp, company: e.target.value })}
                    placeholder="Company Name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Job Title *</label>
                  <Input
                    value={exp.title || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('experience', index, { ...exp, title: e.target.value })}
                    placeholder="Software Engineer"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <Input
                    value={exp.start_date || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('experience', index, { ...exp, start_date: e.target.value })}
                    placeholder="2023"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <Input
                    value={exp.end_date || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('experience', index, { ...exp, end_date: e.target.value })}
                    placeholder="Present"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <Textarea
                  value={exp.description || ''}
                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateArrayField('experience', index, { ...exp, description: e.target.value })}
                  placeholder="Describe your role and responsibilities..."
                  rows={3}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Education */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">🎓 Education</CardTitle>
          <Button
            onClick={() => addArrayItem('education', {
              degree: '',
              institution: '',
              start_date: '',
              end_date: '',
              gpa: '',
              relevant_coursework: []
            })}
            size="sm"
            variant="outline"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Education
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {(formData.education || []).map((edu: Education, index: number) => (
            <div key={index} className="border rounded-lg p-4 space-y-4">
              <div className="flex justify-between items-start">
                <h4 className="font-medium">Education #{index + 1}</h4>
                <Button
                  onClick={() => removeArrayItem('education', index)}
                  size="sm"
                  variant="destructive"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Degree *</label>
                  <Input
                    value={edu.degree || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('education', index, { ...edu, degree: e.target.value })}
                    placeholder="Bachelor of Science in Computer Science"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Institution *</label>
                  <Input
                    value={edu.institution || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('education', index, { ...edu, institution: e.target.value })}
                    placeholder="University Name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                  <Input
                    value={edu.start_date || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('education', index, { ...edu, start_date: e.target.value })}
                    placeholder="2019"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
                  <Input
                    value={edu.end_date || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('education', index, { ...edu, end_date: e.target.value })}
                    placeholder="2023"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">GPA</label>
                  <Input
                    value={edu.gpa || ''}
                    onChange={(e: ChangeEvent<HTMLInputElement>) => updateArrayField('education', index, { ...edu, gpa: e.target.value })}
                    placeholder="3.8/4.0"
                  />
                </div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Skills */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">🛠️ Skills</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Skills (comma-separated)</label>
            <Textarea
              value={(formData.skills || []).join(', ')}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateField('skills', e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s))}
              placeholder="JavaScript, React, Python, Machine Learning, Project Management"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Certifications */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">🏆 Certifications</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Certifications (comma-separated)</label>
            <Textarea
              value={(formData.certifications || []).join(', ')}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateField('certifications', e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s))}
              placeholder="AWS Certified Developer, Google Cloud Professional, PMP"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Languages */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">🌍 Languages</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Languages (comma-separated)</label>
            <Textarea
              value={(formData.languages || []).join(', ')}
              onChange={(e: ChangeEvent<HTMLTextAreaElement>) => updateField('languages', e.target.value.split(',').map((s: string) => s.trim()).filter((s: string) => s))}
              placeholder="English (Native), Spanish (Fluent), French (Intermediate)"
              rows={3}
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-end">
        <Button
          onClick={onExport}
          variant="outline"
          size="lg"
        >
          <Download className="w-4 h-4 mr-2" />
          Export JSON
        </Button>
        <Button
          onClick={handleSave}
          disabled={!hasChanges}
          size="lg"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </Button>
      </div>

      {hasChanges && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800 text-sm">
            ⚠️ You have unsaved changes. Click "Save Changes" to apply them.
          </p>
        </div>
      )}
    </div>
  )
}

export default ResumeFormEditor 