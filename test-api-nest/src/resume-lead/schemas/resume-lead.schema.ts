import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type ResumeLeadDocument = ResumeLead & Document;

@Schema({ collection: 'resume_lead_status' })
export class ResumeLead {
  @Prop({ required: true })
  id: number;

  @Prop({ required: true })
  status: string;

  @Prop({ required: true })
  total: number;
}

export const ResumeLeadSchema = SchemaFactory.createForClass(ResumeLead);
