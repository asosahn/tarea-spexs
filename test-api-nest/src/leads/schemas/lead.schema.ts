import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type LeadDocument = Lead & Document;

@Schema({ collection: 'leads' })
export class Lead {
  @Prop()
  id: string;

  @Prop({ required: true })
  email: string;

  @Prop()
  first_name: string;

  @Prop()
  full_name: string;

  @Prop()
  last_name: string;

  @Prop()
  lead_status: string;

  @Prop()
  lead_status_id: number;
}

export const LeadSchema = SchemaFactory.createForClass(Lead);